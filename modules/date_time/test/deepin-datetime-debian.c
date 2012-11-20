#ifdef HAVE_CONFIG_H
# include "config.h"
#endif

#include "deepin-datetime-debian.h"
#include "deepin-datetime.h"

static void _get_using_ntpdate(gboolean *can_use, gboolean *is_using, GError **error)
{
    if(!g_file_test("/usr/sbin/ntpdate-debian", G_FILE_TEST_EXIST))
        return ;
    *can_use = TRUE;
    
    if(g_file_test("/etc/network/if-up.d/ntpdate", G_FILE_TEST_EXISTS))
        *is_using = TRUE;
}

static void _get_using_ntpd(gboolean *can_use, gboolean *is_using, GError **error)
{
    int exit_status;
    GError *tmp_error = NULL;
    if(!g_file_test("/usr/sbin/ntpd", G_FILE_TEST_EXISTS))
        return ;
    
    *can_use = TRUE;

    if(!g_spawn_command_line_sync("/usr/sbin/service ntp status",
                                  NULL, NULL, &exit_status, &tmp_error)){
        if(error != NULL && *error == NULL){
            *error = g_error_new(DEEPIN_DATETIME_ERROR,
                                 DEEPIN_DATETIME_ERROR_GENERAL,
                                 "Error spawning /usr/sbin/service:%s", tmp_error->message);
        }

        g_error_free(tmp_error);
        return ;
    }

    if(exit_status == 0)
        *is_using = TRUE;
}


gboolean _get_using_ntp_debian(DBusGMethodInvocation *context)
{
    gboolean can_use_ntp = FALSE;
    gboolean is_using_ntp = FALSE;
    GError *error = NULL;

    _get_using_ntpdate(&can_use_ntp, &is_using_ntp, &error);
    _get_using_ntpd(&can_use_ntp, &is_using_ntp, &error);

    if(error == NULL){
        dbus_g_method_return(context, can_use_ntp, is_using_ntp);
        return TRUE;
    }else {
        dbus_g_method_return_error(context, error);
        g_error_free(error);
        return FALSE;
    }
}

static void _set_using_ntpdate(gboolean using_ntp, GError **error)
{
    const gchar *cmd = NULL;
    GError  *tmp_error = NULL;

    /* Debian uses an if-up.d script to sync network time when an interface
       comes up.  This is a separate mechanism from ntpd altogether. */

#define NTPDATE_ENABLED  "/etc/network/if-up.d/ntpdate"
#define NTPDATE_DISABLED "/etc/network/if-up.d/ntpdate.disabled"

    if (using_ntp && g_file_test (NTPDATE_DISABLED, G_FILE_TEST_EXISTS))
        cmd = "/bin/mv -f "NTPDATE_DISABLED" "NTPDATE_ENABLED;
    else if (!using_ntp && g_file_test (NTPDATE_ENABLED, G_FILE_TEST_EXISTS))
        cmd = "/bin/mv -f "NTPDATE_ENABLED" "NTPDATE_DISABLED;
    else
        return;

    if (!g_spawn_command_line_sync (cmd, NULL, NULL, NULL, &tmp_error)) {
        if (error != NULL && *error == NULL) {
            *error = g_error_new (GSD_DATETIME_MECHANISM_ERROR,
                                  GSD_DATETIME_MECHANISM_ERROR_GENERAL,
                                  "Error spawning /bin/mv: %s",
                                  tmp_error->message);
        }
        g_error_free (tmp_error);
        return;
    }

    /* Kick start ntpdate to sync time immediately */
    if (using_ntp &&
        !g_spawn_command_line_sync ("/etc/network/if-up.d/ntpdate",
                                    NULL, NULL, NULL, &tmp_error)) {
        if (error != NULL && *error == NULL) {
            *error = g_error_new (GSD_DATETIME_MECHANISM_ERROR,
                                  GSD_DATETIME_MECHANISM_ERROR_GENERAL,
                                  "Error spawning /etc/network/if-up.d/ntpdate: %s",
                                  tmp_error->message);
        }
        g_error_free (tmp_error);
        return;
    }

}


static void
_set_using_ntpd (gboolean using_ntp, GError **error)
{
    GError *tmp_error = NULL;
    int exit_status;
    char *cmd;

    if (!g_file_test ("/usr/sbin/ntpd", G_FILE_TEST_EXISTS))
        return;

    cmd = g_strconcat ("/usr/sbin/update-rc.d ntp ", using_ntp ? "enable" : "disable", NULL);

    if (!g_spawn_command_line_sync (cmd, NULL, NULL, &exit_status, &tmp_error)) {
        if (error != NULL && *error == NULL) {
            *error = g_error_new (GSD_DATETIME_MECHANISM_ERROR,
                                  GSD_DATETIME_MECHANISM_ERROR_GENERAL,
                                  "Error spawning '%s': %s",
                                  cmd, tmp_error->message);
        }
        g_error_free (tmp_error);
                                                                                                    
        return;
    }

    g_free (cmd);

    cmd = g_strconcat ("/usr/sbin/service ntp ", using_ntp ? "restart" : "stop", NULL);;

    if (!g_spawn_command_line_sync (cmd, NULL, NULL, &exit_status, &tmp_error)) {
        if (error != NULL && *error == NULL) {
            *error = g_error_new (GSD_DATETIME_MECHANISM_ERROR,
                                  GSD_DATETIME_MECHANISM_ERROR_GENERAL,
                                  "Error spawning '%s': %s",
                                  cmd, tmp_error->message);
        }
        g_error_free (tmp_error);
        g_free (cmd);
        return;
    }

    g_free (cmd);
}

gboolean
_set_using_ntp_debian  (DBusGMethodInvocation   *context,
                        gboolean                 using_ntp)
{
    GError *error = NULL;

    /* In Debian, ntpdate and ntpd may be installed separately, so don't
       assume both are valid. */

    _set_using_ntpdate (using_ntp, &error);
    _set_using_ntpd (using_ntp, &error);

    if (error == NULL) {
        dbus_g_method_return (context);
        return TRUE;
    } else {
        dbus_g_method_return_error (context, error);
        g_error_free (error);
        return FALSE;
    }
}

