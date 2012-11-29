#include <Python.h>
#include <polkit/polkit.h>
#include <glib.h>
#include <gio/gio.h>

static PyObject* PolkitPermissionError;

static PyObject* new_sync(PyObject *self, PyObject *args)
{
    const gchar* action_id;
    PolkitSubject* subject;
    PyObject *permission ;
    
    if(!PyArg_ParseTuple(args, "so", &action_id, &subject)){
        return NULL;
    }

    permission =(PyObject *) polkit_permission_new_sync(action_id, subject, NULL, NULL);
    if(!permission){
        return NULL;
    }
    
    return permission;
}


static PyObject* get_action_id(PyObject *self, PyObject *args)
{
    PyObject* action_id;
    PolkitPermission* permission;

    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }
    
    action_id =(PyObject *) polkit_permission_get_action_id(permission);

    if(!action_id){
        return NULL;
    }

    return action_id;
}

static PyObject* get_subject(PyObject *self, PyObject *args)
{
    PyObject *subject;
    PolkitPermission *permission;

    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }

    subject = (PyObject *)polkit_permission_get_subject(permission);

    if(!subject){
        return NULL;
    }

    return subject;
}

static PyObject* get_allowed(PyObject *self, PyObject *args)
{
    gboolean allowed = 0;
    PolkitPermission *permission;
    
    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }

    allowed = g_permission_get_allowed((GPermission *)permission);

    if(allowed){
        return Py_True;
    }else{
        return Py_False;
    }
    
}

static PyObject* get_can_acquire(PyObject *self, PyObject *args)
{
    gboolean acquire = 0;
    PolkitPermission *permission;

    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }
    
    acquire = g_permission_get_can_acquire((GPermission *)permission);

    if(acquire){
        return Py_True;
    } else{
        return Py_False;
    }
}

static PyObject* get_can_release(PyObject *self, PyObject *args)
{
    gboolean release = 0;
    PolkitPermission *permission;

    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }
    
    release = g_permission_get_can_release((GPermission *)permission);

    if(release){
        return Py_True;
    }else{
        return Py_False;
    }
}

static PyObject* acquire(PyObject *self, PyObject *args)
{
    gboolean acquire = 0;
    PolkitPermission *permission;
    
    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }

    acquire = g_permission_acquire((GPermission *)permission, NULL, NULL);

    if(acquire){
        return Py_True;          
    }else{
        return Py_False;
    }

}

static PyObject* release(PyObject *self, PyObject *args)
{
    gboolean release = 0;
    PolkitPermission *permission;

    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }

    release = g_permission_release((GPermission *)permission, NULL, NULL);

    if(release){
        return Py_True;
    }else{
        return Py_False;
    }
}

static PyMethodDef polkitpermission_methods[] = 
{
    {"new_sync", (PyCFunction) new_sync, METH_VARARGS, "create an new Polkit Permission Object"},
    {"get_action_id", (PyCFunction) get_action_id, METH_VARARGS, "get action id"},
    {"get_subject", (PyCFunction) get_subject, METH_VARARGS, "get subject"},
    {"get_allowed", (PyCFunction) get_allowed, METH_VARARGS, "get allowed"},
    {"get_can_acquire", (PyCFunction) get_can_acquire, METH_VARARGS, "get can acquire"},
    {"get_can_release", (PyCFunction) get_can_release, METH_VARARGS, "get can release"},
    {"acquire", (PyCFunction) acquire, METH_VARARGS, "acquire"},
    {"release", (PyCFunction) release, METH_VARARGS, "release"},
    {NULL, NULL, 0, NULL}
};

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC init_polkitpermission(void)
{
    PyObject *m = Py_InitModule3("_polkitpermission", polkitpermission_methods, "module for polkit permission");
    
    if(m == NULL)
        return ;
    
    PolkitPermissionError = PyErr_NewException("polkitpermission.error", NULL, NULL);

    Py_INCREF(PolkitPermissionError);

    PyModule_AddObject(m, "error", PolkitPermissionError);
    
}
