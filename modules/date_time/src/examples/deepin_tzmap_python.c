/* 
 * Copyright (C) 2012 Deepin, Inc.
 *               2012 Zhai Xiang
 *
 * Author:     Zhai Xiang <zhaixiang@linuxdeepin.com>
 * Maintainer: Zhai Xiang <zhaixiang@linuxdeepin.com>
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
 */

#include <Python.h>
#include <cc-timezone-map.h>

/* Safe XDECREF for object states that handles nested deallocations */
#define ZAP(v) do {\
    PyObject *tmp = (PyObject *)(v); \
    (v) = NULL; \
    Py_XDECREF(tmp); \
} while (0)

typedef struct {
    PyObject_HEAD
    PyObject *dict; /* Python attributes dictionary */
    GtkWidget *handle;
} DeepinTzmapObject;

static PyObject *m_deepin_tzmap_object_constants = NULL;
static PyTypeObject *m_DeepinTzmap_Type = NULL;

static DeepinTzmapObject *m_init_deepin_tzmap_object();
static DeepinTzmapObject *m_new(PyObject *self, PyObject *args);

static PyMethodDef deepin_tzmap_methods[] = 
{
    {"new", m_new, METH_VARARGS, "Deepin Tzmap Construction"}, 
    {NULL, NULL, 0, NULL}
};

static PyObject *m_delete(DeepinTzmapObject *self);

static PyMethodDef deepin_tzmap_object_methods[] = 
{
    {"delete", m_delete, METH_NOARGS, "Deepin Tzmap Object Destruction"}, 
    {NULL, NULL, 0, NULL}
};

static void m_deepin_tzmap_dealloc(DeepinTzmapObject *self) 
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
    
    if (!v && dict1)
        v = PyDict_GetItemString(dict1, name);
    if (!v && dict2)
        v = PyDict_GetItemString(dict2, name);
    if (v) {
        Py_INCREF(v);
        return v;
    }
    
    return Py_FindMethod(m, co, name);
}

static int m_setattr(PyObject **dict, char *name, PyObject *v)
{
    if (!v) {
        int rv = -1;
        if (*dict)
            rv = PyDict_DelItemString(*dict, name);
        if (rv < 0) {
            PyErr_SetString(PyExc_AttributeError, 
                            "delete non-existing attribute");
            return rv;
        }
    }
    if (!*dict) {
        *dict = PyDict_New();
        if (!*dict)
            return -1;
    }
    return PyDict_SetItemString(*dict, name, v);
}

static PyObject *m_deepin_tzmap_getattr(DeepinTzmapObject *dgo, 
                                        char *name) 
{
    return m_getattr((PyObject *)dgo, 
                     name, 
                     dgo->dict, 
                     m_deepin_tzmap_object_constants, 
                     deepin_tzmap_object_methods);
}

static PyObject *m_deepin_tzmap_setattr(DeepinTzmapObject *dgo, 
                                        char *name, 
                                        PyObject *v) 
{
    return m_setattr(&dgo->dict, name, v);
}

static PyObject *m_deepin_tzmap_traverse(DeepinTzmapObject *self, 
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

static PyObject *m_deepin_tzmap_clear(DeepinTzmapObject *self) 
{
    ZAP(self->dict);
    return 0;
}

static PyTypeObject DeepinTzmap_Type = {
    PyObject_HEAD_INIT(NULL)
    0, 
    "deepin_tzmap.new", 
    sizeof(DeepinTzmapObject), 
    0, 
    (destructor)m_deepin_tzmap_dealloc,
    0, 
    (getattrfunc)m_deepin_tzmap_getattr, 
    (setattrfunc)m_deepin_tzmap_setattr, 
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
    (traverseproc)m_deepin_tzmap_traverse, 
    (inquiry)m_deepin_tzmap_clear
};

PyMODINIT_FUNC initdeepin_tzmap() 
{
    PyObject *m = NULL;
             
    m_DeepinTzmap_Type = &DeepinTzmap_Type;
    DeepinTzmap_Type.ob_type = &PyType_Type;

    m = Py_InitModule("deepin_tzmap", deepin_tzmap_methods);
    if (!m)
        return;

    m_deepin_tzmap_object_constants = PyDict_New();
}

static DeepinTzmapObject *m_init_deepin_tzmap_object() 
{
    DeepinTzmapObject *self = NULL;

    self = (DeepinTzmapObject *) PyObject_GC_New(DeepinTzmapObject, 
                                                 m_DeepinTzmap_Type);
    if (!self)
        return NULL;
    PyObject_GC_Track(self);

    self->dict = NULL;
    self->handle = NULL;

    return self;
}

static DeepinTzmapObject *m_new(PyObject *dummy, PyObject *args) 
{
    DeepinTzmapObject *self = NULL;
    
    self = m_init_deepin_tzmap_object();
    if (!self)
        return NULL;
    
    self->handle = cc_timezone_map_new();
    
    return self;
}

static PyObject *m_delete(DeepinTzmapObject *self) 
{
    if (self->handle) 
        self->handle = NULL;

    Py_INCREF(Py_None);
    return Py_None;
}
