#ifndef DEEPIN_DATETIME_H
#define DEEPIN_DATETIME_H

#include <glib-object.h>
#include <dbus/dbus-glib.h>

G_BEGIN_DECLS

#define DEEPIN_DATETIME_TYPE                 (deepin_datetime_get_type())
#define DEEPIN_DATETIME(o)                   (G_TYPE_CHECK_INSTANCE_CAST((o), DEEPIN_DATETIME_TYPE, DeepinDatetime))
#define DEEPIN_DATETIME_CLASS(k)             (G_TYPE_CHECK_CLASS_CAST((k), DEEPIN_DATETIME_TYPE, DeepinDatetimeClass))
#define DEEPIN_IS_DATETIME(o)                   (G_TYPE_CHECK_INSTANCE_TYPE((o), DEEPIN_DATETIME_TYPE))
#define DEEPIN_IS_DATETIME_CLASS(k)          (G_TYPE_CHECK_CLASS_TYPE((k), DEEPIN_DATETIME_TYPE))
#define DEEPIN_GET_DATETIME_CLASS(o)         (G_TYPE_INSTANCE_GET_CLASS((o), DEEPIN_DATETIME_TYPE, DeepinDatetimeClass))

typedef struct DeepinDatetimePrivate DeepinDatetimePrivate;

typedef struct 
{
    GObject      parent;
    DeepinDatetimePrivate *priv;
}DeepinDatetime;

typedef struct
{
    GObjectClass parent_class;
}DeepinDatetimeClass;

typedef enum
{
    DEEPIN_DATETIME_ERROR_GENERAL,
    DEEPIN_DATETIME_ERROR_NOT_PRIVILEGED,
    DEEPIN_DATETIME_ERROR_INVALID_TIMEZONE_FILE,
    DEEPIN_DATETIME_NUM_ERRORS
}DeepinDatetimeError;

#define DEEPIN_DATETIME_ERROR   deepin_datetime_error_quark()

GType deepin_datetime_error_get_type(void);

#define DEEPIN_DATETIME_TYPE_ERROR (deepin_datetime_error_get_type())

GQuark deepin_datetime_error_quark(void);

GType  deepin_datetime_get_type(void);

DeepinDatetime * deepin_datetime_new(void);

gboolean deepin_datetime_get_timezone(DeepinDatetime *datetime, DBusGMethodInvocation *context);

gboolean deepin_datetime_set_timezone(DeepinDatetime *datetime, const char *zone_file, DBusGMethodInvocation *context);

gboolean deepin_datetime_can_set_timezone(DeepinDatetime *datetime, DBusGMethodInvocation *context);

gboolean deepin_datetime_set_time(DeepinDatetime *datetime, gint64 seconds_since_epoch, DBusGMethodInvocation *context);

gboolean deepin_datetime_set_date(DeepinDatetime *datetime, guint day, guint month, guint year, DBusGMethodInvocation *context);

gboolean deepin_datetime_can_set_time(DeepinDatetime *datetime, DBusGMethodInvocation *context);

gboolean deepin_datetime_adjust_time(DeepinDatetime *datetime, gint64 seconds_to_add, DBusGMethodInvocation *context);

gboolean deepin_datetime_get_hardware_clock_using_utc (DeepinDatetime *datetime, DBusGMethodInvocation *context);

gboolean deepin_datetime_set_hardware_clock_using_utc (DeepinDatetime *datetime, gboolean using_utc, DBusGMethodInvocation *context);
gboolean deepin_datetime_get_using_ntp(DeepinDatetime *datetime, DBusGMethodInvocation *context);

gboolean deepin_datetime_set_using_ntp(DeepinDatetime *datetime, gboolean using_ntp, DBusGMethodInvocation *context);

gboolean deepin_datetime_can_set_using_ntp(DeepinDatetime *datetime, DBusGMethodInvocation *context);

G_END_DECLS

#endif
