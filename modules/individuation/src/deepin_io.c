/* 
 * Copyright (C) 2013 Deepin, Inc.
 *               2013 Zhai Xiang
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
#include <dirent.h>

#define ERROR(v) PyErr_SetString(PyExc_TypeError, v)
#define STRING(v) PyString_FromString(v)

static PyObject *m_walk_images(PyObject *self, PyObject *args);

static PyMethodDef deepin_io_methods[] = 
{
    {"walk_images", m_walk_images, 0, "Deepin walk through images directory"}, 
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initdeepin_io() 
{
    PyObject *m = NULL;

    m = Py_InitModule("deepin_io", deepin_io_methods);
    if (!m)
        return;
}

static int m_is_filter_dir(char *fn, PyObject *filter_dir) 
{
    int i;

    for (i = 0; i < PyList_Size(filter_dir); i++) {
        if (strcmp(fn, PyString_AsString(PyList_GetItem(filter_dir, i))) == 0) 
            return 1;
    }

    return 0;
}

static void m_walk_dir(char *root_dir, PyObject *image_paths, PyObject *filter_dir) 
{
    DIR *dp = NULL;
    struct dirent *ep = NULL;
    struct stat st;
    char fn[FILENAME_MAX];
    int len = strlen(root_dir);

    if (len >= FILENAME_MAX - 1) {
        printf("filename is tooo long\n");
        return;
    }

    dp = opendir(root_dir);                                                     
    if (!dp) {                                                                  
        printf("opendir(%s) failed\n", root_dir);                               
        return;
    }

    strcpy(fn, root_dir);
    fn[len++] = '/';

    while (ep = readdir(dp)) {                                                  
        if (strcmp(ep->d_name, ".") == 0 || strcmp(ep->d_name, "..") == 0)      
            continue;

        strncpy(fn + len, ep->d_name, FILENAME_MAX - len);
        if (m_is_filter_dir(fn, filter_dir)) 
            continue;

        if (lstat(fn, &st) == -1) 
            continue;
 
        if (S_ISLNK(st.st_mode))                                                
            continue;                                                           
                                                                                
        if (S_ISDIR(st.st_mode))                                                
            m_walk_dir(fn, image_paths, filter_dir);

        PyList_Append(image_paths, STRING(fn));
    }                                                                           
    
    if (dp) {   
        closedir(dp);                                                               
        dp = NULL;
    }
}

static PyObject *m_walk_images(PyObject *self, PyObject *args) 
{
    char *root_dir = NULL;
    PyObject *filter_type = NULL;
    PyObject *filter_dir = NULL;
    PyObject *image_paths = NULL;

    if (!PyArg_ParseTuple(args, "sOO", &root_dir, &filter_type, &filter_dir)) {
        ERROR("invalid arguments to walk_images");
        return NULL;
    }

    if (!PyList_Check(filter_type)) 
        Py_RETURN_NONE;

    if (!PyList_Check(filter_dir)) 
        Py_RETURN_NONE;

    image_paths = PyList_New(0);
    m_walk_dir(root_dir, image_paths, filter_dir);

    return image_paths;
}
