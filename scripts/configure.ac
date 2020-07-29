AC_INIT([open_pdks], [1.0], [github.com/RTimothyEdwards/open_pdks])

# detect PDKs based on directories that include Makefile.in files
m4_define([M4_GET_TECHS], [m4_normalize(m4_esyscmd(cd .. && find * -mindepth 1 -name "Makefile.in" -exec dirname {} \; | tr "\n" " "))])

AC_DEFUN([M4_GEN_WITH_PDK_SOURCE_ARGS],
[
    # --with-pdk-source=PDK_SOURCE_PATH
    m4_foreach_w(pdk, $1, [
        AC_MSG_NOTICE([Checking whether 'pdk' is specified])
        AC_ARG_WITH(pdk-source,
              [AS_HELP_STRING([--with-pdk-source=/path/to/pdk/source], "location of the source files for pdk")],
              [
               pdk[]_SOURCE_PATH=$with_[]pdk[]_source
               AC_MSG_NOTICE([Checking specified path for 'pdk' at $[]pdk[]_SOURCE_PATH])

               # force an absolute path
               # pdk[]_SOURCE_PATH=$(readlink -f $[]pdk[]_SOURCE_PATH)

               # basic check that the PDK exists there (the path must exist in any case)
               AC_CHECK_FILE($[]pdk[]_SOURCE_PATH,
                       [
                        AC_MSG_NOTICE(['pdk' source path found at $[]pdk[]_SOURCE_PATH])
                       ],
                       [
                        AC_MSG_ERROR([Specified path for 'pdk' at $[]pdk[]_SOURCE_PATH not found])
                       ]
               )
              ]
        )
        AC_SUBST([]pdk[]_SOURCE_PATH)
    ])
])

AC_MSG_NOTICE([Found technology directories: M4_GET_TECHS()])

M4_GEN_WITH_PDK_SOURCE_ARGS(M4_GET_TECHS())

# --with-local-path=LOCAL_PATH
AC_ARG_WITH(local-path,
      [AS_HELP_STRING([--with-local-path=/path/to/install/pdks], "location where the PDKs will be installed")],
      [
       LOCAL_PATH=$with_local_path
       AC_MSG_NOTICE([Local installation path set to $LOCAL_PATH])
      ],
      [
       AC_MSG_ERROR([--with-local-path=/path/to/install/pdks is a required argument])
      ]
)
AC_SUBST(LOCAL_PATH)



# Checking if (some) prerequisites are satisfied
AM_PATH_PYTHON([3.4])
AX_PYTHON_MODULE(distutils)

AC_PATH_PROG(MAGIC, magic)
if test -z "$MAGIC"; then
   AC_MSG_ERROR([You need 'magic' to generate the needed various cell views])
fi



MAKEFILES=$(find .. -name "Makefile.in" | sed 's/\(.*\)\.in/\1/g')
AC_CONFIG_FILES($MAKEFILES)

AC_OUTPUT

AC_MSG_RESULT(Build configured successfully)
