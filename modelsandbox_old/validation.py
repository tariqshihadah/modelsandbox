from cerberus import Validator


class ExtendedValidator(Validator):
    
    def _validate_less_than(self, other_fields, field, value):
        """
        Check that the field value is less than the value of the other field.

        The rule's arguments are validated against this schema:
        {'type': ['string', 'list']}
        """
        if isinstance(other_fields, str):
            other_fields = [other_fields]
        for other_field in other_fields:
            if other_field not in self.document:
                self._error(field, "Could not be checked against %s, not provided" % (other_field))
            elif not (value < self.document[other_field]):
                self._error(field, "Must be less than '%s'" % (other_field))

    def _validate_less_than_equal(self, other_fields, field, value):
        """
        Check that the field value is less than or equal to the value of 
        the other field.

        The rule's arguments are validated against this schema:
        {'type': ['string', 'list']}
        """
        if isinstance(other_fields, str):
            other_fields = [other_fields]
        for other_field in other_fields:
            if other_field not in self.document:
                self._error(field, "Could not be checked against %s, not provided" % (other_field))
            elif not (value <= self.document[other_field]):
                self._error(field, "Must be less than or equal to '%s'" % (other_field))

    def _validate_greater_than(self, other_fields, field, value):
        """
        Check that the field value is greater than the value of the other field.

        The rule's arguments are validated against this schema:
        {'type': ['string', 'list']}
        """
        if isinstance(other_fields, str):
            other_fields = [other_fields]
        for other_field in other_fields:
            if other_field not in self.document:
                self._error(field, "Could not be checked against %s, not provided" % (other_field))
            elif not (value > self.document[other_field]):
                self._error(field, "Must be greater than '%s'" % (other_field))

    def _validate_greater_than_equal(self, other_fields, field, value):
        """
        Check that the field value is greater than or equal to the value of 
        the other field.

        The rule's arguments are validated against this schema:
        {'type': ['string', 'list']}
        """
        if isinstance(other_fields, str):
            other_fields = [other_fields]
        for other_field in other_fields:
            if other_field not in self.document:
                self._error(field, "Could not be checked against %s, not provided" % (other_field))
            elif not (value >= self.document[other_field]):
                self._error(field, "Must be greater than or equal to '%s'" % (other_field))

    def _validate_equal(self, other_fields, field, value):
        """
        Check that the field value is equal to the value of the other field.

        The rule's arguments are validated against this schema:
        {'type': ['string', 'list']}
        """
        if isinstance(other_fields, str):
            other_fields = [other_fields]
        for other_field in other_fields:
            if other_field not in self.document:
                self._error(field, "Could not be checked against %s, not provided" % (other_field))
            elif not (value == self.document[other_field]):
                self._error(field, "Must be equal to '%s'" % (other_field))

    def _validate_not_equal(self, other_fields, field, value):
        """
        Check that the field value is not equal to the value of the other field.

        The rule's arguments are validated against this schema:
        {'type': ['string', 'list']}
        """
        if isinstance(other_fields, str):
            other_fields = [other_fields]
        for other_field in other_fields:
            if other_field not in self.document:
                self._error(field, "Could not be checked against %s, not provided" % (other_field))
            elif not (value != self.document[other_field]):
                self._error(field, "Must not be equal to '%s'" % (other_field))
