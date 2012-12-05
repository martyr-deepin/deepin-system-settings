/* 
 * Copyright (C) 2012 Deepin, Inc.
 *               2012 Long Wei
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
#include <structmember.h>

#include <gio/gdesktopappinfo.h>

typedef struct{
    PyObject_HEAD
    gchar *filename;    

    GDesktopAppInfo *info;    
}App;

static int App_traverse(App *self, visitproc visit, void *arg)
{
    /* int vret; */
    /* if(self->filename){ */
    /*     vret = visit(self->filename, arg); */
    /*     if(vret != 0){ */
    /*         return vret; */
    /*     } */
    /* } */

    /* if(self->info){ */
    /*     vret = visit(self->info, arg); */
    /*     if(vret != 0){ */
    /*         return vret; */
    /*     } */
    /* } */

    /* Py_VISIT(self->filename); */
    /* Py_VISIT(self->info); */

    return 0;
}

static int App_clear(App *self)
{
    /* PyObject *tmp; */
    
    /* tmp = self->filename; */
    /* self->filename = NULL; */
    /* Py_XDECREF(tmp); */

    /* tmp = self->info; */
    /* self->info = NULL; */
    /* Py_XDECREF(tmp); */
    Py_CLEAR(self->filename);
    Py_CLEAR(self->info);

    return 0;
}

static void App_dealloc(App *self)
{
    App_clear(self);
    self->ob_type->tp_free((PyObject *)self);
}

static PyObject *App_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    App *self;
    const char *desktop_id;

    if(!PyArg_ParseTuple(args, "s", &desktop_id)){
        return -1;
    }
    
    self = (App *)type->tp_alloc(type, 0);

    if(self != NULL){
        if(desktop_id != NULL){
            self->info = g_desktop_app_info_new(desktop_id);

            if(self->info == NULL){
                Py_DECREF(self);
                return NULL;
            }
        }
    }
    return (PyObject *)self;
}

static int App_init(App *self, PyObject *args, PyObject *kwds)
{
    gchar *filename;
    GDesktopAppInfo *info;
    PyObject *tmp;

    static char *kwlist[] = {"filename", "info", NULL};

    if (! PyArg_ParseTupleAndKeywords(args, kwds, "|sO", kwlist, 
                                      &filename, &info))
        return -1; 

    if (filename != NULL) {
        tmp = self->filename;
        Py_INCREF(filename);
        self->filename = filename;
        Py_XDECREF(tmp);
    }

    if (info != NULL) {
        tmp = self->info;
        Py_INCREF(info);
        self->info = info;
        Py_XDECREF(info);
    }

    return 0;
}

static PyMemberDef App_members[] = {
    {"filename", T_OBJECT_EX, offsetof(App, filename), 0, "file name"},
    {"info", T_OBJECT_EX, offsetof(App, info), 0, "info"},

    {NULL}  /* Sentinel */
};

static PyObject * App_hello(App *self)
{
    printf("Hello World!\n");

    return Py_True;
}

static PyObject * App_get_default_for_type(App *self, PyObject *args)
{
    const char *content_type ;
    gboolean must_support_uris = 0;
    
    GAppInfo *default_app;
    const char *default_app_id;

    if(!PyArg_ParseTuple(args, "s|i", &content_type, &must_support_uris)){
        return -1;
    }

    if(content_type == NULL){
        return -1;
    }

    default_app = g_app_info_get_default_for_type(content_type, must_support_uris);
    
    if(default_app == NULL){
            return -1;
        }

    default_app_id = g_app_info_get_id(default_app);

    if(default_app_id){
        return Py_BuildValue("s", default_app_id);
    }
}

static PyObject * App_get_recommended_for_type(App *self, PyObject *args)
{
    const char *content_type ;
    

    if(!PyArg_ParseTuple(args, "s", &content_type)){
        return -1;
    }

    if(content_type == NULL){
        return -1;
    }

    ;
}

static PyObject * App_set_default_for_type(App *self, PyObject *args)
{
    const char *content_type ;
    gboolean ret;

    if(!PyArg_ParseTuple(args, "s", &content_type)){
        return -1;
    }

    if(content_type == NULL){
        return -1;
    }

    if(self->info == NULL){
        return -1;
    }

    ret = g_app_info_set_as_default_for_type(self->info, content_type, NULL);

    if(ret){
        return Py_True;
    }else{
        return Py_False;
    }
}

static PyMethodDef App_methods[] = {
    {"hello", (PyCFunction)App_hello, METH_NOARGS, "Just Say Hello World for test"},
    {"get_default", (PyCFunction)App_get_default_for_type, METH_VARARGS, "get default app for content type"},
    {"get_recommended", (PyCFunction)App_get_recommended_for_type, METH_VARARGS, "get recommended app for content type"},
    {"set_default", (PyCFunction)App_set_default_for_type, METH_VARARGS, "set app as default for content type"},
    {NULL}  /* Sentinel */
};

static PyTypeObject AppType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "gdesktopapp.app",             /*tp_name*/
    sizeof(App),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)App_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC, /*tp_flags*/
    "App objects",           /* tp_doc */
    (traverseproc)App_traverse,   /* tp_traverse */
    (inquiry)App_clear,           /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    App_methods,             /* tp_methods */
    App_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)App_init,      /* tp_init */
    0,                         /* tp_alloc */
    App_new,                 /* tp_new */
};

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initgdesktopapp(void) 
{
    PyObject* m;

    g_type_init();

    if (PyType_Ready(&AppType) < 0)
        return;

    m = Py_InitModule3("gdesktopapp", module_methods,
                       "Example module that creates an extension type.");

    if (m == NULL)
        return;

    Py_INCREF(&AppType);
    PyModule_AddObject(m, "App", (PyObject *)&AppType);
}
