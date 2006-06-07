#ifdef _PROTOTYPE_

#define land_method(_returntype, _name, _params) _returntype (*_name)_params
#define land_call_method(self, method, params) if (self->vt->method) self->vt->method params

#endif /* _PROTOTYPE_ */

#include "util.h"
