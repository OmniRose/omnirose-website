from django.db import models
from django.db.models import Max, Min
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

import warnings

import numpy
from scipy.optimize import curve_fit, OptimizeWarning

from accounts.models import User

from .equations import all_equations

def mod360(angle):
    return angle % 360

class ErrorNoSuitableEquationAvailable(Exception):
    pass



class CurveCalculations(object):

    curve_equation = None

    curve_opt = None
    curve_cov = None

    _min_deviation = None
    _max_deviation = None

    _readings_as_dict = None

    @property
    def can_calculate_curve(self):
        number_of_points = len(self.readings_as_dict.values())
        return number_of_points >= 3

    @property
    def min_deviation(self):
        self._find_max_and_min_deviation_if_needed()
        return self._min_deviation

    @property
    def max_deviation(self):
        self._find_max_and_min_deviation_if_needed()
        return self._max_deviation


    def _find_max_and_min_deviation_if_needed(self):
        if self._min_deviation is not None and self._max_deviation is not None:
            return

        # Get the highest and lowest values from the readings as a starting
        # point
        deviations = self.readings_as_dict.values()
        min_dev = min(deviations)
        max_dev = max(deviations)

        # Would be nice to do this a little less brute forcish
        for degree in range(1, 360):
            dev = self.deviation_at(degree)
            if dev < min_dev: min_dev = dev
            if dev > max_dev: max_dev = dev

        padding = 0.05
        self._min_deviation = int(numpy.floor(min_dev - padding))
        self._max_deviation = int(numpy.ceil(max_dev + padding))


    def deviation_at(self, heading):
        """Calculate the deviation for the given heading"""
        self.calculate_curve_if_needed()

        popt = self.curve_opt
        accurate = self.curve_equation(heading, *popt)
        return round(accurate, 3)


    def compass_to_magnetic(self, compass):
        magnetic = compass + self.deviation_at(compass)
        return mod360(magnetic)

    def magnetic_to_compass(self, magnetic, max_delta=0.0001, round_ndigits=3, max_iterations=50):

        iteration_count = 0
        compass = magnetic

        while True:
            reverse_mag = self.compass_to_magnetic(compass)
            delta = (reverse_mag - magnetic)

            # Are we accurate enough?
            if abs(delta) < max_delta:
                break

            # check that we've not gone too long
            if iteration_count > max_iterations:
                break
            iteration_count = iteration_count + 1

            compass = (compass - delta * 0.9) % 360

        rounded = round(compass, round_ndigits)
        return mod360(rounded)

    def magnetic_to_true(self, magnetic, variation=0):
        true = magnetic + variation
        return mod360(true)

    def true_to_magnetic(self, true, variation=0):
        magnetic = true - variation
        return mod360(magnetic)

    def compass_to_true(self, compass, variation=0):
        magnetic = self.compass_to_magnetic(compass)
        true = self.magnetic_to_true(magnetic, variation)
        return mod360(true)

    def true_to_compass(self, true, variation=0):
        magnetic = self.true_to_magnetic(true, variation)
        compass  = self.magnetic_to_compass(magnetic)
        return mod360(compass)


    def calculate_curve_if_needed(self):
        if not self.curve_has_been_calculated():
            return self.calculate_curve()

    def curve_has_been_calculated(self):
        return bool(self.curve_opt is not None)

    @property
    def readings_as_dict(self):
        return self._readings_as_dict


    def suitable_equations(self):
        point_count = len( self.readings_as_dict.values() )

        suitable = []
        for data in all_equations:
            if data['points_needed'] <= point_count:
                suitable.append(data)
        return suitable


    def choose_equation(self):
        try:
            return self.suitable_equations()[0]['equation']
        except IndexError:
            raise ErrorNoSuitableEquationAvailable("No suitable equation could be found for this curve")

    @classmethod
    def equations_as_choices(cls, equations):
        choices = []
        for data in equations:
            choices.append(( data['slug'], data['name']))
        return choices

    @classmethod
    def all_equations_as_choices(cls):
        return cls.equations_as_choices(all_equations)

    def suitable_equations_as_choices(self):
        return self.equations_as_choices(self.suitable_equations())

    def calculate_curve(self):

        self._min_deviation = None
        self._max_deviation = None

        headings   = []
        deviations = []

        for ships_head, deviation in self.readings_as_dict.items():
            headings.append(ships_head)
            deviations.append(deviation)

        # Work out which equation to use
        equation = self.choose_equation()

        with warnings.catch_warnings():
            # We might get an "OptimizeWarning" that we want to ignore
            warnings.simplefilter("ignore", category=OptimizeWarning)
            popt, pcov = curve_fit(equation, numpy.array(headings), numpy.array(deviations))

        self.curve_equation = equation
        self.curve_opt = popt
        self.curve_cov = pcov


class Curve(CurveCalculations, models.Model):

    user   = models.ForeignKey(User, blank=True, null=True)

    vessel = models.CharField(
        max_length=80,
        verbose_name="Vessel's Name",
        help_text='e.g. "SV Gypsy Moth"',
    )
    note = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Note",
        help_text='e.g. "Steering compass" or "with radio mounted on binnacle"',
    )
    equation_slug = models.CharField(
        max_length=80,
        choices=CurveCalculations.all_equations_as_choices(),
        blank=True
    )

    unlocked = models.DateTimeField(editable=False, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s (%s)" % (self.vessel, self.note)

    def get_absolute_url(self):
        return reverse('curve_detail', args=[str(self.id)])

    @property
    def readings_as_dict(self):
        readings = self.reading_set.all().order_by('ships_head')
        as_dict = {}
        for reading in readings:
            as_dict[reading.ships_head] = reading.deviation
        return as_dict

    def choose_equation(self):
        # Do we have an equation stored that we should try to use?
        preferred_equation_slug = self.equation_slug
        if preferred_equation_slug:
            for choice in self.suitable_equations():
                if preferred_equation_slug == choice['slug']:
                    return choice['equation']

        # If we could not find one then let the code find the best one
        return super(Curve, self).choose_equation()


    def set_unlocked_to_now(self):
        self.unlocked = timezone.now()
        return None

    @property
    def is_unlocked(self):
        return bool(self.unlocked)


class Reading(models.Model):
    curve = models.ForeignKey(Curve)
    ships_head = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(359)])
    deviation = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])

    class Meta():
        ordering = ['ships_head']

    def __unicode__(self):
        return "(%g, %g)" % (self.ships_head, self.deviation)



