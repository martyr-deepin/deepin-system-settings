#include <Python.h>
#include <polkit/polkit.h>
#include <glib.h>
#include <gio/gio.h>

/* Safe XDECREF for object states that handles nested deallocations */
#define ZAP(v) do {                             \
        PyObject *tmp = (PyObject *)(v);        \
        (v) = NULL;                             \
        Py_XDECREF(tmp);                        \
    } while (0)

typedef struct{
    PyObject_HEAD
    PyObject *dict;
    PolkitPermission *handle;

}PolkitPermissionObject;

static PyObject *m_polkit_permission_object_constants = NULL;
static PyTypeObject *m_PolkitPermission_Type = NULL;

static PolkitPermissionObject *m_init_polkit_permission_object();
static PolkitPermissionObject *m_new(PyObject *self, PyObject *args);

static PyMethodDef polkit_permission_methods[] = 
{
    {"new", m_new, METH_VARARGS, "Polkit Permission Object Construct"},
    {NULL, NULL, 0, NULL}
};

static PyObject *m_delete(PolkitPermissionObject *self);
static PyObject *get_action_id(PolkitPermissionObject *self);
static PyObject *get_subject(PolkitPermissionObject *self);
static PyObject *get_allowed(PolkitPermissionObject *self);
static PyObject *get_can_acquire(PolkitPermissionObject *self);
static PyObject *get_can_release(PolkitPermissionObject *self);
static PyObject *acquire(PolkitPermissionObject *self);
static PyObject *release(PolkitPermissionObject *self);

static PyMethodDef polkit_permission_object_methods[] = 
{
    {"delete", (PyCFunction) m_delete, METH_VARARGS, "PolkitPermissionObject destruction"},
    {"get_action_id", (PyCFunction) get_action_id, METH_VARARGS, "get action id"},
    {"get_subject", (PyCFunction) get_subject, METH_VARARGS, "get subject"},
    {"get_allowed", (PyCFunction) get_allowed, METH_VARARGS, "get allowed"},
    {"get_can_acquire", (PyCFunction) get_can_acquire, METH_VARARGS, "get can acquire"},
    {"get_can_release", (PyCFunction) get_can_release, METH_VARARGS, "get can release"},
    {"acquire", (PyCFunction) acquire, METH_VARARGS, "acquire"},
    {"release", (PyCFunction) release, METH_VARARGS, "release"},
    {NULL, NULL, 0, NULL}
};

static void m_polkit_permission_dealloc(PolkitPermissionObject *self)
{
    PyObject_GC_UnTrack(self);
    Py_TRASHCAN_SAFE_BEGIN(self)

    ZAP(self->dict);
    m_delete(self);

    PyObject_GC_Del(self);
    Py_TRASHCAN_SAFE_END(self)

}

static PyObject *m_getattr(PyObject *co, 
                           char *name, 
                           PyObject *dict1, 
                           PyObject *dict2, 
                           PyMethodDef *m)
{
    PyObject *v = NULL;
    if (v == NULL && dict1 != NULL)
        v = PyDict_GetItemString(dict1, name);
    if (v == NULL && dict2 != NULL)
        v = PyDict_GetItemString(dict2, name);
    if (v != NULL) {
        Py_INCREF(v);
        return v;
    }
    return Py_FindMethod(m, co, name);
}

static int m_setattr(PyObject **dict, char *name, PyObject *v)
{
    if (v == NULL) {
        int rv = -1;
        if (*dict != NULL)
            rv = PyDict_DelItemString(*dict, name);
        if (rv < 0) {
            PyErr_SetString(PyExc_AttributeError, 
                            "delete non-existing attribute");
            return rv;
        }
    }
    if (*dict == NULL) {
        *dict = PyDict_New();
        if (*dict == NULL)
            return -1;
    }
    return PyDict_SetItemString(*dict, name, v);
}


static PyObject *m_polkit_permission_getattr(PolkitPermissionObject *ppo,
                                            char *name) 
{
    return m_getattr((PyObject *)ppo, 
                     name, 
                     ppo->dict, 
                     m_polkit_permission_object_constants, 
                     polkit_permission_object_methods);
}

static PyObject *m_polkit_permission_setattr(PolkitPermissionObject *ppo, 
                                            char *name, 
                                            PyObject *v) 
{
    return m_setattr(&ppo->dict, name, v);
}

static PyObject *m_polkit_permission_traverse(PolkitPermissionObject *self, 
                                             visitproc visit, 
                                             void *args) 
{
    int err;
#undef VISIT
#define VISIT(v)    if ((v) != NULL && ((err = visit(v, args)) != 0)) return err

    VISIT(self->dict);

    return 0;
#undef VISIT
}

static PyObject *m_polkit_permission_clear(PolkitPermissionObject *self) 
{
    ZAP(self->dict);
    return 0;
}

static PyTypeObject PolkitPermission_Type = {
    PyObject_HEAD_INIT(NULL)
    0, 
    "polkit_permission.new", 
    sizeof(PolkitPermissionObject), 
    0, 
    (destructor)m_polkit_permission_dealloc,
    0, 
    (getattrfunc)m_polkit_permission_getattr, 
    (setattrfunc)m_polkit_permission_setattr, 
    0, 
    0, 
    0,  
    0,  
    0,  
    0,  
    0,  
    0,  
    0,  
    0,  
    Py_TPFLAGS_HAVE_GC,
    0,  
    (traverseproc)m_polkit_permission_traverse, 
    (inquiry)m_polkit_permission_clear
};

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC initpolkit_permission()
{
    PyObject *m = NULL;
             
    m_PolkitPermission_Type = &PolkitPermission_Type;
    PolkitPermission_Type.ob_type = &PyType_Type;

    m = Py_InitModule("polkit_permission", polkit_permission_methods);
    if (!m)
        return;

    m_polkit_permission_object_constants = PyDict_New();
}

static PolkitPermissionObject *m_init_polkit_permission_object() 
{
    PolkitPermissionObject *self = NULL;

    self = (PolkitPermissionObject *) PyObject_GC_New(PolkitPermissionObject,
                                                     m_PolkitPermission_Type);
    if (!self)
        return NULL;
    PyObject_GC_Track(self);

    self->dict = NULL;
    self->handle = NULL;

    return self;
}

static PolkitPermissionObject *m_new(PyObject *dummy, PyObject *args) 
{
    PolkitPermissionObject *self = NULL;
    const gchar *action_id = NULL;
    
    self = m_init_polkit_permission_object();
    if (!self)
        return NULL;

    if (!PyArg_ParseTuple(args, "s", &action_id))
        return NULL;

    g_type_init ();
    
    self->handle = polkit_permission_new_sync(action_id, NULL, NULL, NULL);

    return self;
}

static PyObject *m_delete(PolkitPermissionObject *self) 
{
    if (self->handle) {
        g_object_unref(self->handle);
        self->handle = NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* get_action_id(PolkitPermissionObject *self)
{
    const gchar *action_id;

    if(!self->handle){
        return NULL;
    }
    
    action_id = polkit_permission_get_action_id(self->handle);

    if(!action_id){
        return NULL;
    }

    return Py_BuildValue("s", action_id);
}

static PyObject* get_subject(PolkitPermissionObject *self)
{
    PolkitSubject *subject;

    if(!self->handle){
        return NULL;
    }

    subject = polkit_permission_get_subject(self->handle);

    if(!subject){
        return NULL;
    }

    return subject;
}

static PyObject* get_allowed(PolkitPermissionObject *self)
{
    gboolean allowed = 0;

    if(!self->handle){
        return NULL;
    }

    allowed = g_permission_get_allowed((GPermission *)self->handle);

    if(allowed){
        return Py_True;
    }else{
        return Py_False;
    }
    
}

static PyObject* get_can_acquire(PolkitPermissionObject *self)
{
    gboolean acquire = 0;

    if(!self->handle){
        return NULL;
    }

    acquire = g_permission_get_can_acquire((GPermission *)self->handle);

    if(acquire){
        return Py_True;
    } else{
        return Py_False;
    }
}

static PyObject* get_can_release(PolkitPermissionObject *self)
{
    gboolean release = 0;

    if(!self->handle){
        return NULL;
    }

    release = g_permission_get_can_release((GPermission *)self->handle);

    if(release){
        return Py_True;
    }else{
        return Py_False;
    }
}

static PyObject* acquire(PolkitPermissionObject *self)
{
    gboolean acquire = 0;

    if(!self->handle){
        return NULL;
    }

    acquire = g_permission_acquire((GPermission *)self->handle, NULL, NULL);

    if(acquire){
        return Py_True;          
    }else{
        return Py_False;
    }

}

static PyObject* release(PolkitPermissionObject *self)
{
    gboolean release = 0;

    if(!self->handle){
        return NULL;
    }

    release = g_permission_release((GPermission *)self->handle, NULL, NULL);

    if(release){
        return Py_True;
    }else{
        return Py_False;
    }
}

