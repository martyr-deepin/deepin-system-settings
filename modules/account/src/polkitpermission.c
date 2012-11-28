#include <Python.h>
#include <polkit/polkit.h>
#include <glib.h>
#include <gio.h>

static PyObject* PolkitPermissionError;

static PyObject* new_sync(PyObject *self, PyObject *args)
{
    const gchar* action_id;
    PolkitSubject* subject;
    PyObject *permission ;
    
    if(!PyArg_ParseTuple(args, "so", &action_id, &subject)){
        return NULL;
    }

    permission = polkit_permission_new_sync(action_id, subject, None, None);
    if(!permission){
        return NULL;
    }
    
    return permission;
}

static PyObject* get_action_id(PyObject *self, PyObject *args)
{
    const gchar* action_id;
    PolkitPermission* permission;

    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }
    
    action_id = polkit_permission_get_action_id(permission);

    if(!action_id){
        return NULL;
    }

    return action_id;
}

static PyObject* get_subject(PyObject *self, PyObject *args)
{
    PolkitSubject *subject;
    PolkitPermission *permission;

    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }

    subject = polkit_permission_get_subject(permission);

    if(!subject){
        return NULL;
    }

    return subject;
}

static PyObject* get_allowed(PyObject *self, PyObject *args)
{
    gboolean allowed;
    PolkitPermission *permission;
    
    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }

    allowed = g_permission_get_allowed((GPermission *)permission);

    return allowed;
}

static PyObject* get_can_acquire(PyObject *self, PyObject *args)
{
    gboolean acquire;
    PolkitPermission *permission;

    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }
    
    acquire = g_permission_get_can_acquire((GPermission *)permission);

    return acquire;
}

static PyObject* get_can_release(PyObject *self, PyObject *args)
{
    gboolean release;
    PolkitPermission *permission;

    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }
    
    release = g_permission_get_can_release((GPermission *)permission);

    return release;
}

static PyObject* acquire(PyObject *self, PyObject *args)
{
    gboolean acquire;
    PolkitPermission *permission;
    
    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }

    acquire = g_permission_acquire((GPermission *)permission, None, None);

    return acquire;
}

static PyObject* release(PyObject *self, PyObject *args)
{
    gboolean release;
    PolkitPermission *permission;

    if(!PyArg_ParseTuple(args, "o", &permission)){
        return NULL;
    }

    release = g_permission_release((GPermission *)permission, None, None);

    return release;
}

static PyMethodDef polkitpermission_methods[] = 
{
    {"new_sync", new_sync, METH_VARARGS, "create an new Polkit Permission Object"},
    {"get_action_id", get_action_id, METH_VARARGS, "get action id"},
    {"get_subject", get_subject, METH_VARARGS, "get subject"},
    {"get_allowed", get_allowed, METH_VARARGS, "get allowed"},
    {"get_can_acquire", get_can_acquire, METH_VARARGS, "get can acquire"},
    {"get_can_release", get_can_release, METH_VARARGS, "get can release"},
    {"acquire", acquire, METH_VARARGS, "acquire"},
    {"release", release, METH_VARARGS, "release"},
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
