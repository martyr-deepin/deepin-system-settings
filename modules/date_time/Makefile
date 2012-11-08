CC = gcc

all:
	$(CC) -c gsd-datetime-mechanism.c `pkg-config --cflags --libs glib-2.0 dbus-glib-1 policykit-1`
	$(CC) -c system-timezone.c `pkg-config --cflags --libs glib-2.0 dbus-glib-1`
	$(CC) -c gsd-datetime-mechanism-main.c `pkg-config --cflags --libs glib-2.0 dbus-glib-1`
	$(CC) -o gsd-datetime-mechanism gsd-datetime-mechanism.o system-timezone.o gsd-datetime-mechanism-main.o `pkg-config --libs glib-2.0 dbus-glib-1`

clean:
	rm -f gsd-datetime-mechanism gsd-datetime-mechanism.0 system-timezone.o gsd-datetime-mechanism-main.o
