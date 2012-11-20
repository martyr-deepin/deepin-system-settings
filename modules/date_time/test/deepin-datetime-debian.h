#include <glib.h>
#include <dbus/dbus-glib.h>

gboolean _get_using_ntp_debian(DBusGMethodInvocation *context);

gboolean _set_using_ntp_debian(DBusGMethodInvocation *context, gboolean using_ntp);
