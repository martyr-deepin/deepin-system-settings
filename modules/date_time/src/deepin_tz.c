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
#include <time.h>

#define INT(v) PyInt_FromLong(v)

static PyObject *m_gmtoff(PyObject *self, PyObject *args);

static PyMethodDef deepin_tz_methods[] = 
{
    {"gmtoff", m_gmtoff, 0, "Deepin timezone get gmtoff"}, 
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initdeepin_tz() 
{
    PyObject *m = NULL;

    m = Py_InitModule("deepin_tz", deepin_tz_methods);
    if (!m)
        return;
}

static PyObject *m_gmtoff(PyObject *self, PyObject *args) 
{
    time_t cur_time = time(NULL);
    struct tm *local_tm = localtime(&cur_time);

    return INT(local_tm->tm_gmtoff / 3600);
}
