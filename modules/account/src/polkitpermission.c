/* 
 * Copyright (C) 2012 ~ 2013 Deepin, Inc.
 *               2012 ~ 2013 Long Wei
 *
 * Author:     Long Wei <yilang2007lw@gmail.com>
 * Maintainer: Long Wei <yilang2007lw@gmail.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include <Python.h>
#include <polkit/polkit.h>
#include <glib.h>
#include <gio/gio.h>

typedef struct{
    PyObject_HEAD
    PolkitPermission *permission;
    PyObject *action_id;

}PolkitPermissionObject;

static PyObject *PolkitPermissionError;
static void pypolkit_permission_dealloc(PolkitPermissionObject *);
static int  pypolkit_permission_traverse(PolkitPermissionObject *self, visitproc visit, void *arg);
static int  pypolkit_permission_clear(PolkitPermissionObject *);
static int  pypolkit_permission_init(PolkitPermissionObject *, PyObject *, PyObject *);
static PyObject *pypolkit_permission_new(PyTypeObject *type, PyObject *args, PyObject *kwds);

static PyObject *polkitpermission_get_action_id(PolkitPermissionObject *self);
static PyObject *polkitpermission_get_allowed(PolkitPermissionObject *self);
static PyObject *polkitpermission_get_can_acquire(PolkitPermissionObject *self);
static PyObject *polkitpermission_get_can_release(PolkitPermissionObject *self);
static PyObject *polkitpermission_acquire(PolkitPermissionObject *self);
static PyObject *polkitpermission_release(PolkitPermissionObject *self);

static PyMethodDef polkitpermission_object_methods[] =
{
    {"get_action_id", (PyCFunction) polkitpermission_get_action_id, METH_NOARGS, "get action id"},
    {"get_allowed", (PyCFunction) polkitpermission_get_allowed, METH_NOARGS, "get allowed"},
    {"get_can_acquire", (PyCFunction) polkitpermission_get_can_acquire, METH_NOARGS, "get can acquire"},
    {"get_can_release", (PyCFunction) polkitpermission_get_can_release, METH_NOARGS, "get can release"},
    {"acquire", (PyCFunction) polkitpermission_acquire, METH_NOARGS, "acquire"},
    {"release", (PyCFunction) polkitpermission_release, METH_NOARGS, "release"},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject pypolkit_permission_Type_obj = {
    PyObject_HEAD_INIT(&PyType_Type)
    .tp_name = "polkitpermission",
    .tp_basicsize = sizeof(PolkitPermissionObject),
    /* .tp_itemsize = XXX */
    .tp_dealloc = (destructor) pypolkit_permission_dealloc,
    /* .tp_getattr = XXX */
    /* .tp_setattr = XXX */
    /* .tp_compare = (cmpfunc) _pypolkit_PolkitPermission_compare, */
    /* .tp_repr = XXX */
    /* .tp_as_number = XXX */
    /* .tp_as_sequence = XXX */
    /* .tp_as_mapping = XXX */
    .tp_hash = PyObject_HashNotImplemented,
    .tp_call = NULL,
    /* .tp_str = (reprfunc) _pypolkit_PolkitPermission_str, */
    .tp_getattro = PyObject_GenericGetAttr,
    .tp_setattro = PyObject_GenericSetAttr,
    /* .tp_as_buffer = XXX */
    .tp_flags = Py_TPFLAGS_HAVE_CLASS | Py_TPFLAGS_CHECKTYPES |
    Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_BASETYPE,
    /* .tp_doc = "polkit PolkitPermission doc", */
    .tp_traverse = (traverseproc) pypolkit_permission_traverse,
    .tp_clear = (inquiry) pypolkit_permission_clear,
    /* .tp_richcompare = (richcmpfunc) _pypolkit_PolkitPermission_richcompare, */
    /* .tp_weaklistoffset = XXX */
    /* .tp_iter = XXX */
    /* .tp_iternext = XXX */
    .tp_methods = polkitpermission_object_methods,
    /* .tp_members = XXX */
    /* .tp_getset = XXX */
    .tp_base = NULL,
    .tp_dict = NULL,
    /* .tp_descr_get = XXX */
    /* .tp_descr_set = XXX */
    /* .tp_dictoffset = XXX */
    .tp_init = (initproc) pypolkit_permission_init,
    .tp_alloc = PyType_GenericAlloc,
    .tp_new = pypolkit_permission_new,
    /* .tp_free = XXX */
    /* .tp_is_gc = XXX */
    .tp_bases = NULL,
    /* .tp_del = XXX */
};

static void pypolkit_permission_dealloc(PolkitPermissionObject *self){

    pypolkit_permission_clear(self);
    self->ob_type->tp_free((PyObject *)self);
}

static int pypolkit_permission_traverse(PolkitPermissionObject *self, visitproc visit, void *arg){

    Py_VISIT(self->action_id);
    return 0;
}

static int pypolkit_permission_clear(PolkitPermissionObject *self){

    Py_CLEAR(self->action_id);
    return 0;
}

static int pypolkit_permission_init(PolkitPermissionObject *self, PyObject *args, PyObject *kwds){

    PyObject *tmp, *action_id;
    const gchar *action;

    if(!PyArg_ParseTuple(args, "s", &action)){
        return -1;
    }

    if(action){
        action_id = Py_BuildValue("s", action);
        
        tmp = self->action_id;
        Py_INCREF(action_id);
        self->action_id = action_id;
        Py_XDECREF(tmp);

        if(self->permission){
            self->permission = NULL;
            g_object_unref(self->permission);
        }

        self->permission = (PolkitPermission *) polkit_permission_new_sync(action, NULL, NULL, NULL);
    }
    return 0;
}

static PyObject* pypolkit_permission_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PolkitPermissionObject *self;

    self = (PolkitPermissionObject *)type->tp_alloc(type, 0);
    if(self != NULL){
        self->action_id = PyString_FromString("");
        if(self->action_id == NULL){
            Py_DECREF(self);
            return NULL;
        }

        self->permission = NULL;
    }
    return (PyObject *)self;
}

static PyMethodDef polkitpermission_module_methods[] = 
{
    {NULL, NULL, 0, NULL}
};

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC 
initpolkitpermission(void){
    PyObject *m = NULL;
    m = Py_InitModule3("polkitpermission", polkitpermission_module_methods, "python binding for polkit permission");

    if(!m){
        return ;
    }

    g_type_init();

    if(PyType_Ready(&pypolkit_permission_Type_obj) < 0){
        return ;
    }

    Py_INCREF(&pypolkit_permission_Type_obj);
    PyModule_AddObject(m, "new_with_action", (PyObject *)&pypolkit_permission_Type_obj); 

    PolkitPermissionError = PyErr_NewException("polkitpermission.error", NULL, NULL);
    PyModule_AddObject(m, "error", PolkitPermissionError);
}

static PyObject* polkitpermission_get_action_id(PolkitPermissionObject *self)
{
    const gchar *action_id;

    if(!self->permission){
        PyErr_SetString(PolkitPermissionError, "assert permission failed in get action id");
        return NULL;
    }

    action_id = polkit_permission_get_action_id(self->permission);

    if(!action_id){
        PyErr_SetString(PolkitPermissionError, "get action id failed");
        return NULL;
    }

    return Py_BuildValue("s", action_id);
}

static PyObject* polkitpermission_get_allowed(PolkitPermissionObject *self)
{
    gboolean allowed = 0;

    if(!self->permission){
        PyErr_SetString(PolkitPermissionError, "assert permission failed in get allowed");
        return NULL;
    }

    allowed = g_permission_get_allowed((GPermission *)self->permission);

    if(allowed){
        Py_INCREF(Py_True);
        return Py_True;
    }else{
        Py_INCREF(Py_False);
        return Py_False;
    }
}

static PyObject* polkitpermission_get_can_acquire(PolkitPermissionObject *self)
{
    gboolean acquire = 0;

    if(!self->permission){
        PyErr_SetString(PolkitPermissionError, "assert permission failed in get can acquire");
        return NULL;
    }

    acquire = g_permission_get_can_acquire((GPermission *)self->permission);

    if(acquire){
        Py_INCREF(Py_True);
        return Py_True;
    } else{
        Py_INCREF(Py_False);
        return Py_False;
    }
}

static PyObject* polkitpermission_get_can_release(PolkitPermissionObject *self)
{
    gboolean release = 0;

    if(!self->permission){
        PyErr_SetString(PolkitPermissionError, "assert permission failed in get can release");
        return NULL;
    }

    release = g_permission_get_can_release((GPermission *)self->permission);

    if(release){
        Py_INCREF(Py_True);
        return Py_True;
    }else{
        Py_INCREF(Py_False);
        return Py_False;
    }
}

static PyObject* polkitpermission_acquire(PolkitPermissionObject *self)
{
    gboolean acquire = 0;

    if(!self->permission){
        PyErr_SetString(PolkitPermissionError, "assert permission failed in acquire");
        return NULL;
    }

    acquire = g_permission_acquire((GPermission *)self->permission, NULL, NULL);

    if(acquire){
        Py_INCREF(Py_True);
        return Py_True;
    }else{
        Py_INCREF(Py_False);
        return Py_False;
    }

}

static PyObject* polkitpermission_release(PolkitPermissionObject *self)
{
    gboolean release = 0;

    if(!self->permission){
        PyErr_SetString(PolkitPermissionError, "assert permission failed in release");
        return NULL;
    }

    release = g_permission_release((GPermission *)self->permission, NULL, NULL);

    if(release){
        Py_INCREF(Py_True);
        return Py_True;
    }else{
        Py_INCREF(Py_False);
        return Py_False;
    }
}
