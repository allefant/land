macro land_method(_returntype, _name, _params) _returntype (*_name)_params
macro land_call_method(self, method, params) if (self->vt->method) self->vt->method params
