#ifdef HAVE_CONFIG_H
# include "config.h"
#endif

#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>
#include <errno.h>
#include <sys/time.h>

#include <dbus/dbus-glib.h>
#include <dbus/dbus-glib-lowlevel.h>

#include <polkit/polkit.h>

#include "system-timezone.h"
#include "deepin-datetime.h"
#include "deepin-datetime-glue.h"

#include "deepin-datetime-debian.h"


static gboolean
do_exit (gpointer user_data)
{
    g_debug ("Exiting due to inactivity");
    exit (1);
    return FALSE;
}

static void
reset_killtimer (void)
{
    static guint timer_id = 0;

    if (timer_id > 0) {
        g_source_remove (timer_id);
    }
    g_debug ("Setting killtimer to 30 seconds...");
    timer_id = g_timeout_add_seconds (30, do_exit, NULL);
}

struct DeepinDatetimePrivate
{
    DBusGConnection *system_bus_connection;
    DBusGProxy      *system_bus_proxy;
    PolkitAuthority *auth;
};

static void deepin_datetime_finalize (GObject *object);

G_DEFINE_TYPE (DeepinDatetime, deepin_datetime, G_TYPE_OBJECT)

#define DEEPIN_DATETIME_GET_PRIVATE(o) (G_TYPE_INSTANCE_GET_PRIVATE((o), DEEPIN_DATETIME_TYPE, DeepinDatetimePrivate))

GQuark deepin_datetime_error_quark(void)
{
    static GQuark ret = 0;
    if(ret == 0){
        ret = g_quark_from_static_string("deepin datetime error");
    }
    return ret;
}


#define ENUM_ENTRY(NAME, DESC) {NAME, "" #NAME "", DESC}

GType deepin_datetime_error_get_type(void)
{
    static GType etype = 0;
    if(etype == 0){
        static const GEnumValue values[] = {
            ENUM_ENTRY(DEEPIN_DATETIME_ERROR_GENERAL, "GeneralError"),
            ENUM_ENTRY(DEEPIN_DATETIME_ERROR_NOT_PRIVILEGED, "NotPrivileged"),
            ENUM_ENTRY(DEEPIN_DATETIME_ERROR_INVALID_TIMEZONE_FILE, "InvalidTimezoneFile"),
            {0, 0, 0}
        };

        g_assert(DEEPIN_DATETIME_NUM_ERRORS == G_N_ELEMENTS(values) - 1);

        etype = g_enum_register_static("DeepinDatetimeError", values);
    }

    return etype;
}

static GObject * deepin_datetime_constructor(GType type, guint n_construct_properties, GObjectConstructParam *construct_properties)
{
    DeepinDatetime *datetime;
    datetime = DEEPIN_DATETIME(G_OBJECT_CLASS(deepin_datetime_parent_class)->constructor(
                                   type, n_construct_properties, construct_properties));

    return G_OBJECT(datetime);
}

static void deepin_datetime_class_init(DeepinDatetimeClass *klass)
{
    GObjectClass *object_class = G_OBJECT_CLASS(klass);
    
    object_class->constructor = deepin_datetime_constructor;
    object_class->finalize = deepin_datetime_finalize;

    g_type_class_add_private(klass, sizeof(DeepinDatetimePrivate));

    dbus_g_object_type_install_info(DEEPIN_DATETIME_TYPE, &dbus_glib_deepin_datetime_object_info);
    
    dbus_g_error_domain_register(DEEPIN_DATETIME_ERROR, NULL, DEEPIN_DATETIME_TYPE_ERROR);
}

static void deepin_datetime_init(DeepinDatetime *datetime)
{
    datetime->priv = DEEPIN_DATETIME_GET_PRIVATE(datetime);
}

static void deepin_datetime_finalize(GObject *object)
{
    DeepinDatetime *datetime;
    
    g_return_if_fail(object != NULL);
    g_return_if_fail(DEEPIN_IS_DATETIME(object));

    datetime = DEEPIN_DATETIME(object);

    g_return_if_fail(datetime->priv != NULL);
    
    g_object_unref(datetime->priv->system_bus_proxy);
    
    G_OBJECT_CLASS(deepin_datetime_parent_class)->finalize(object);
}

static gboolean register_datetime(DeepinDatetime *datetime)
{
    GError *error = NULL;
    
    datetime->priv->auth = polkit_authority_get_sync(NULL, &error);
    if(datetime->priv->auth == NULL){
        if(error != NULL){
            g_critical("error getting system bus:%s", error->message);
            g_error_free(error);
        }
        goto error;
    }

    datetime->priv->system_bus_connection = dbus_g_bus_get(DBUS_BUS_SYSTEM, &error);
    if(datetime->priv->system_bus_connection == NULL){
        if(error != NULL){
            g_critical("error getting system bus:%s", error->message);
            g_error_free(error);
        }
        goto error;
    }
    
    dbus_g_connection_register_g_object(datetime->priv->system_bus_connection, "/", 
                                        G_OBJECT(datetime));

    datetime->priv->system_bus_proxy = dbus_g_proxy_new_for_name (datetime->priv->system_bus_connection,
                                                                  DBUS_SERVICE_DBUS,
                                                                  DBUS_PATH_DBUS,
                                                                  DBUS_INTERFACE_DBUS);

    reset_killtimer();

    return TRUE;

error:
    return FALSE;

}


DeepinDatetime * deepin_datetime_new(void)
{
    GObject *object;
    gboolean res;
    
    object = g_object_new(DEEPIN_DATETIME_TYPE, NULL);

    res = register_datetime(DEEPIN_DATETIME(object));
    if(!res){
        g_object_unref(object);
        return NULL;
    }

    return DEEPIN_DATETIME(object);
}

static gboolean _check_polkit_for_action(DeepinDatetime *datetime, DBusGMethodInvocation *context)
{
    const char *action = "com.linuxdeepin.datetime.configure";
    const char *sender;
    GError *error;
    PolkitSubject *subject;
    PolkitAuthorizationResult *result;
    
    error = NULL;

    sender = dbus_g_method_get_sender(context);
    subject = polkit_system_bus_name_new(sender);

    result = polkit_authority_check_authorization_sync(datetime->priv->auth,
                                                       subject, 
                                                       action,
                                                       NULL,
                                                       POLKIT_CHECK_AUTHORIZATION_FLAGS_ALLOW_USER_INTERACTION,
                                                       NULL,
                                                       &error);
    
    g_object_unref(subject);

    if(error){
        dbus_g_method_return_error(context, error);
        g_error_free(error);

        return FALSE;
    }

    if( !polkit_authorization_result_get_is_authorized(result)){
        error = g_error_new(DEEPIN_DATETIME_ERROR,
                            DEEPIN_DATETIME_ERROR_NOT_PRIVILEGED,
                            "Not Authorized for action %s", action);

        dbus_g_method_return_error(context, error);
        g_error_free(error);
        g_object_unref(result);
        return FALSE;
       }

    g_object_unref(result);
    
    return TRUE;
    
}

static gboolean _sync_hwclock(DBusGMethodInvocation *context)
{
    GError *error;
    error = NULL;

    if(g_file_test("/sbin/hwclock", G_FILE_TEST_EXISTS| G_FILE_TEST_IS_REGULAR | G_FILE_TEST_IS_EXECUTABLE)){
        int exit_status;
        
        if(!g_spawn_command_line_sync("/sbin/hwclock --systohc", NULL, NULL, &exit_status, &error)){
            GError *error2;
            error2 = g_error_new(DEEPIN_DATETIME_ERROR,
                                 DEEPIN_DATETIME_ERROR_GENERAL,
                                 "Error spawning /sbin/hwclock:%s", error->message);
            g_error_free(error);
            
            dbus_g_method_return_error(context, error2);
            return FALSE;
        }
        if(WEXITSTATUS(exit_status) != 0){
            error = g_error_new(DEEPIN_DATETIME_ERROR,
                                DEEPIN_DATETIME_ERROR_GENERAL,
                                "/sbin/hwclock returned %d", exit_status);
            
            dbus_g_method_return_error(context, error);
            g_error_free(error);
            return FALSE;
        }
    }

    return TRUE;
}

static gboolean _set_time(DeepinDatetime *datetime, const struct timeval *tv, DBusGMethodInvocation *context)
{
    GError *error;
    if(!_check_polkit_for_action(datetime, context))
        return FALSE;

    if(settimeofday(tv, NULL) != 0){
        error = g_error_new(DEEPIN_DATETIME_ERROR,
                            DEEPIN_DATETIME_ERROR_GENERAL,
                            "Error calling settimeofday({%lld, %lld}):%s",
                            (long long int)tv->tv_sec, (long long int) tv->tv_usec,
                            strerror(errno));

        dbus_g_method_return_error(context, error);
        g_error_free(error);
        return FALSE;
    }

    if(!_sync_hwclock(context))
        return FALSE;
    
    dbus_g_method_return(context);
    
    return TRUE;
}

static gboolean _set_date(DeepinDatetime *datetime, guint day, guint month, guint year, DBusGMethodInvocation *context)
{
    GDateTime *time;
    char *date_str, *time_str;
    char *date_cmd;
    int exit_status;
    GError *error;
    
    date_str = g_strdup_printf("%02d/%02d/%02d", month, day, year);
    
    error = NULL;

    time = g_date_time_new_now_local();
    time_str = g_date_time_format(time, "%R:%S");
    g_date_time_unref(time);

    date_cmd = g_strdup_printf ("/bin/date -s \"%s %s\" +\"%%D %%R:%%S\"", date_str, time_str);
    g_free(date_str);
    g_free(time_str);

    if(!g_spawn_command_line_sync(date_cmd, NULL, NULL, &exit_status, &error)){
        GError *error2;
        error2 = g_error_new(DEEPIN_DATETIME_ERROR,
                             DEEPIN_DATETIME_ERROR_GENERAL,
                             "Error spawning /bin/date:%s", error->message);

        g_error_free(error);
        dbus_g_method_return_error(context, error2);
        g_error_free(error2);
        g_free(date_cmd);
        return FALSE;
    }
    g_free(date_cmd);
    
    if(WEXITSTATUS(exit_status) != 0){
        error = g_error_new(DEEPIN_DATETIME_ERROR,
                            DEEPIN_DATETIME_ERROR_GENERAL,
                            "/bin/date return %d", exit_status);
        
        dbus_g_method_return_error(context, error);
        g_error_free(error);
        return FALSE;
    }

    if(!_sync_hwclock(context))
        return FALSE;

    return TRUE;
}

gboolean deepin_datetime_set_time(DeepinDatetime *datetime, gint64 seconds_since_epoch, DBusGMethodInvocation *context)
{
    struct timeval tv;
    reset_killtimer();

    g_debug ("SetTime(%" G_GINT64_FORMAT ") called", seconds_since_epoch);
    
    tv.tv_sec = (time_t) seconds_since_epoch;
    tv.tv_usec = 0;
    return _set_time(datetime, &tv, context);

}

gboolean deepin_datetime_set_date(DeepinDatetime *datetime, guint day, guint month, guint year, DBusGMethodInvocation *context)
{
    reset_killtimer();
    g_debug ("SetDate(%d, %d, %d) called", day, month, year);

    return _set_date(datetime, day, month, year, context);
}

gboolean deepin_datetime_adjust_time(DeepinDatetime *datetime, gint64 seconds_to_add, DBusGMethodInvocation *context)
{
    struct timeval tv;
    reset_killtimer();

    g_debug ("AdjustTime(%" G_GINT64_FORMAT " ) called", seconds_to_add);
    
    if(gettimeofday(&tv, NULL) != 0){
        GError *error;
        error = g_error_new(DEEPIN_DATETIME_ERROR,
                            DEEPIN_DATETIME_ERROR_GENERAL,
                            "Error calling gettimeofday(）:%s", strerror(errno));

        dbus_g_method_return_error(context, error);
        g_error_free(error);
        return FALSE;
    }

    tv.tv_sec += (time_t) seconds_to_add;
    return _set_time(datetime, &tv, context);
}

static gboolean deepin_datetime_check_tz_name(const char *tz, GError **error)
{
    GFile *file;
    char *tz_path, *actual_path;
    gboolean retval;
    
    retval = TRUE;
    tz_path = g_build_filename(SYSTEM_ZONEINFODIR, tz, NULL);

    file = g_file_new_for_path(tz_path);
    actual_path = g_file_get_path(file);

    g_obejct_unref(file);

    if(g_strcmp0(tz_path, actual_path) != 0){
        g_set_error(error, DEEPIN_DATETIME_ERROR,
                    DEEPIN_DATETIME_ERROR_INVALID_TIMEZONE_FILE,
                    "Timezone file '%s' was invalid",
                    tz);
        
        retval = FALSE;
    }

    g_free(tz_path);
    g_free(actual_path);

    return retval;
}

gboolean deepin_datetime_set_timezone(DeepinDatetime *datetime, const char *tz, DBusGMethodInvocation *context)
{
    GError *error;
    reset_killtimer();

    g_debug ("SetTimezone('%s') called", tz);

    if(!_check_polkit_for_action(datetime, context))
        return FALSE;

    error = NULL;

    if(!deepin_datetime_check_tz_name(tz, &error))
        return FALSE;

    if(!system_timezone_set(tz, &error)){
        GError *error2;
        int code;
        
        if(error->code == SYSTEM_TIMEZONE_ERROR_INVALIE_TIMEZONE_FILE)
            code = DEEPIN_DATETIME_ERROR_INVALID_TIMEZONE_FILE;
        else
            code = DEEPIN_DATETIME_ERROR_GENERAL;

        error2 = g_error_new(DEEPIN_DATETIME_ERROR,
                             code, "%s", error->message);

        g_error_free(error);

        dbus_g_method_return_error(context, error2);
        g_error_free(error2);

        return FALSE;
    }

    dbus_g_method_return(context);
   
    return TRUE;
}

gboolean deepin_datetime_get_timezone(DeepinDatetime *datetime, DBusGMethodInvocation *context)
{
    gchar *timezone;
    
    reset_killtimer();
    
    timezone = system_timezone_find();

    dbus_g_method_return(context, timezone);
    
    reutrn TRUE;
}

gboolean deepin_datetime_get_hardware_clock_using_utc(DeepinDatetime *datetime, DBusGMethodInvocation *context)
{
    char **lines;
    char *data;
    gsize len;
    GError *error;
    gboolean is_utc;

    error = NULL;
    if(!g_file_get_contents("/etc/adjtime", &data, &len, &error)){
        GError *error2;
        error2 = g_error_new(DEEPIN_DATETIME_ERROR,
                             DEEPIN_DATETIME_ERROR_GENERAL,
                             "Error reading /etc/adjtime file:%s", error->message);

        g_error_free(error);
        dbus_g_method_return_error(context, error2);
        g_error_free(error2);

        return FALSE;
    }

    lines = g_strsplit(data,"\n", 0);
    g_free(data);

    if(g_strv_length(lines) < 3){
        error = g_error_new(DEEPIN_DATETIME_ERROR,
                            DEEPIN_DATETIME_ERROR_GENERAL,
                            "Cannot parse /etc/adjtime");

        dbus_g_method_return_error(context, error);
        
        g_error_free(error);
        g_strfreev(lines);
        return FALSE;
    }

    if(strcmp(lines[2], "UTC") == 0){
        is_utc = TRUE;
    }else if(strcmp(lines[2], "LOCAL") == 0){
        is_utc = FALSE;
    }else{
        error = g_error_new(DEEPIN_DATETIME_ERROR,
                            DEEPIN_DATETIME_ERROR_GENERAL,
                            "Expected UTC or LOCAL at line 3 of /etc/adjtime; found '%s'", lines[2]);

        dbus_g_method_return_error(context, error);

        g_error_free(error);
        g_strfreev(lines);
        return FALSE;
    }

    g_strfreev(lines);

    dbus_g_method_return(context, is_utc);
    return TRUE;
}

gboolean deepin_datetime_set_hardware_clock_using_utc(DeepinDatetime *datetime,gboolean using_utc, DBusGMethodInvocation *context)
{
    GError *error;
    error = NULL;
    
    if(!_check_polkit_for_action(mechanism, context))
        return FALSE;
    
    if(g_file_test("/sbin/hwclock", G_FILE_TEST_EXISTS | G_FILE_TEST_IS_REGULAR | G_FILE_TEST_IS_EXECUTABLE)){
        int exit_status;
        char *cmd;
        cmd = g_strdup_printf("/sbin/hwclock %s --systohc", using_utc ? "--utc" : "--localtime");
        if(!g_spawn_command_line_sync(cmd, NULL, NULL, &exit_status, &error)){
            GError *error2;
            error2 = g_error_new(DEEPIN_DATETIME_ERROR,
                                 DEEPIN_DATETIME_ERROR_GENERAL,
                                 "Error spawning /sbin/hwclock:%s", error->message);

            g_error_free(error);
            dbus_g_method_return_error(context, error2);
            g_error_free(error2);
            g_free(cmd);
            return FALSE;
        }

        g_free(cmd);
        if(WEXITSTATUS(exit_status) != 0){
            error = g_error_new(DEEPIN_DATETIME_ERROR,
                                DEEPIN_DATETIME_ERROR_GENERAL,
                                "/sbin/hwclock returned %d", exit_status);
            dbus_g_method_return_error(context, error);
            g_error_free(error);
            return FALSE;
        }
    }
    dbus_g_method_return(context);
    return TRUE;
}

gboolean deepin_datetime_get_using_ntp(DeepinDatetime *datetime, DBusGMethodInvocation *context)
{
    GError *error = NULL;
    gboolean ret;
    
    if(g_file_test("/usr/sbin/update-rc.d", G_FILE_TEST_EXISTS))
        ret = _get_using_ntp_debian(context);
    else{
        error = g_error_new(DEEPIN_DATETIME_ERROR,
                            DEEPIN_DATETIME_ERROR_GENERAL,
                            "Error enabling NTP:OS varinat not supported");

        dbus_g_method_return_error(context, error);
        g_error_free(error);
        return FALSE;
    }
    return ret;
}

gboolean deepin_datetime_set_using_ntp(DeepinDatetime *datetime, gboolean using_ntp, DBusGMethodInvocation *context)
{
    GError *error;
    gboolean ret;
    
    error = NULL;
    if(!_check_polkit_for_action(datetime, context))
        return FALSE;
    
    if(g_file_test("/usr/sbin/update-rc.d", G_FILE_EXISTS))
        ret = _set_using_ntp_debian(context, using_ntp);
    else{
        error = g_error_new(DEEPIN_DATETIME_ERROR,
                            DEEPIN_DATETIME_ERROR_GENERAL,
                            "Error enabling NTP:os variant not supported");

        dbus_g_method_return_error(context, error);
        g_error_free(error);
        return FALSE;
    }
    return ret;
}

static void check_can_do(DeepinDatetime *datetime, const char *action, DBusGMethodInvocation *context)
{
    const char *sender;
    PolkitSubject *subject;
    PolkitAuthorizationResult *result;
    GError *error;
    
    sender = dbus_g_method_get_sender(context);
    subject = polkit_system_bus_name_new(sender);

    error = NULL;

    result = polkit_authority_check_authorization_sync(datetime->priv->auth,
                                                       subject, action, NULL, 0, NULL, &error);

    g_object_unref(subject);

    if(error){
        dbus_g_method_return_error(context, error);
        g_error_free(error);
        return;
    }

    if(polkit_authorization_result_get_is_authorized(result)){
        dbus_g_method_return(context, 2);
    }else if(polkit_authorization_result_get_is_challenge(result)){
        dbus_g_method_return(context, 1);
    }else{
        dbus_g_method_return(context, 0);
    }

    g_object_unref(result);
}

gboolean deepin_datetime_can_set_time(DeepinDatetime *datetime, DBusGMethodInvocation *context)
{
    check_can_do(datetime, "com.linuxdeepin.datetime.configure", context);
    
    return TRUE;
}

gboolean deepin_datetime_can_set_timezone(DeepinDatetime *datetime, DBusGMethodInvocation *context)
{
    check_can_do(datetime, "com.linuxdeepin.datetime.configure", context);
    
    return TRUE;
}

gboolean deepin_datetime_can_set_using_ntp(DeepinDatetime *datetime, DBusGMethodInvocation *context)
{
    check_can_do(datetime, "com.linuxdeepin.datetime.configure", context);

    return TRUE;
}
