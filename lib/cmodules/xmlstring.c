/***********************************************************************
 * Copyright 2016 Uche Ogbuji (USA)
 ***********************************************************************/

static char module_doc[] = "\
Miscellaneous XML-specific string functions\n\
\n\
Copyright 2016 Uche Ogbuji (USA).\n\
";

/*
#define PY_SSIZE_T_CLEAN
*/
#include <Python.h>

#define XmlString_BUILDING_MODULE
#include "xmlstring.h"

/* header generated from gencharset.py */
#include "charset.h"

/* Borrows boilerplate from https://docs.python.org/3/howto/cporting.html */
struct module_state {
    PyObject *error;
};

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

/** Private Routines **************************************************/

#define IS_XMLSPACE(c) (((c) == 0x09) || \
                        ((c) == 0x0A) || \
                        ((c) == 0x0D) || \
                        ((c) == 0x20))


static char isxml_doc[] =
"isxml(S) -> bool\n\
S must be a bytes object, not unicode/string\
\n\
Return True if the given bytes represent a (possibly) well-formed XML\n\
document. (see http://www.w3.org/TR/REC-xml/#sec-guessing).";

static PyObject *string_isxml(PyObject *self, PyObject *args)
{
  /*
    #See this article about XML detection heuristics
    #http://www.xml.com/pub/a/2007/02/28/what-does-xml-smell-like.html
  */
  char *str, *encoding;
  int len;
  PyObject *characters, *result;
  Py_UNICODE *p;

  if (!PyArg_ParseTuple(args,"y#:isxml", &str, &len))
    return NULL;

  /* Determine the encoding of the XML bytes */
  if (len >= 4) {
    Py_UCS4 ch = (((unsigned char)str[0] << 24)
                  | ((unsigned char)str[1] << 16)
                  | ((unsigned char)str[2] << 8)
                  | (unsigned char)str[3]);
    switch (ch) {
    case 0x3C3F786D: /* '<?xm' */
    case 0x003C003F: /* '<?' UTF-16BE */
    case 0x3C003F00: /* '<?' UTF-16LE */
    case 0x4C6FA794: /* '<?xm' EBCDIC */
    case 0x0000003C: /* '<' UCS-4 (1234 order) [big-endian] */
    case 0x3C000000: /* '<' UCS-4 (4321 order) [little-endian] */
    case 0x00003C00: /* '<' UCS-4 (2143 order) [unusual] */
    case 0x003C0000: /* '<' UCS-4 (3412 order) [unusual] */
      Py_RETURN_TRUE;
    case 0x0000FEFF: /* BOM UCS-4 (1234 order) [big-endian] */
    case 0xFFFE0000: /* BOM UCS-4 (4321 order) [little-endian] */
    case 0x0000FFFE: /* BOM UCS-4 (2143 order) [unusual] */
    case 0xFEFF0000: /* BOM UCS-4 (3412 order) [unusual] */
      /* NOTE - this is not a valid Python codec (as of 2.4).  It is still
       * OK to use as failure to lookup here (and return a False result) is
       * the same as the parser not being able to handle it later.
       */
      encoding = "utf-32";
      break;
    default:
      /* check for UTF-8 BOM */
      if ((ch & 0xFFFFFF00) == 0xEFBBBF00) {
        /* Skip over the BOM as Python includes it in the result */
        encoding = "utf-8";
        str += 3;
        len -= 3;
      } else {
        switch (ch >> 16) {
        case 0xFEFF: /* BOM UTF-16BE */
        case 0xFFFE: /* BOM UTF-16LE */
          encoding = "utf-16";
          break;
        default: /* UTF-8 without encoding declaration */
          encoding = "utf-8";
        }
      }
    }
  } else {
    /* UTF-8 without encoding declaration */
    encoding = "utf-8";
  }

  characters = PyUnicode_Decode(str, len, encoding, NULL);
  if (characters == NULL) {
    /* The auto-detected encoding is not correct, must not be XML */
    PyErr_Clear();
    result = Py_False;
  } else {
    /* Find the first non-whitespace character */
    p = PyUnicode_AS_UNICODE(characters);
    /* while (*p && IS_XMLSPACE(*p)) {printf("ASCII value = %d, Character = [%c]\n", *p, *p); p++;} */
    while (IS_XMLSPACE(*p)) p++;

    /* The first non-whitespace character in a well-formed XML document must
     * be '<'.
     */
    result = *p == '<' ? Py_True : Py_False;
    Py_DECREF(characters);
  }

  Py_INCREF(result);
  return result;
}

/** Module Initialization *********************************************/


static PyMethodDef module_methods[] = {
  { "isxml",      (PyCFunction)string_isxml,      METH_VARARGS, isxml_doc },
  { NULL, NULL }
};

static int module_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int module_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "cxmlstring",
        module_doc,
        sizeof(struct module_state),
        module_methods,
        NULL,
        module_traverse,
        module_clear,
        NULL
};

#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_cxmlstring(void)
{
    PyObject *module = PyModule_Create(&moduledef);

    if (module == NULL)
        INITERROR;
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("cxmlstring.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

    return module;
}
