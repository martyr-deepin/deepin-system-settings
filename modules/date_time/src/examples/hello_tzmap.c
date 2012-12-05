#include "cc-timezone-map.h"

int main(int argc, char **argv)
{
    GtkWidget *window;
    GtkWidget *map;
    GtkWidget *fixed;

    gtk_init(&argc, &argv);

    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "cc-timezone-map widget");
    gtk_window_set_position(GTK_WINDOW(window), GTK_WIN_POS_CENTER);
    gtk_window_set_default_size(GTK_WINDOW(window), 400, 300);

    g_signal_connect(G_OBJECT(window), "destroy", G_CALLBACK(gtk_main_quit), NULL);

    map = (GtkWidget *) cc_timezone_map_new();
    gtk_container_add(GTK_CONTAINER(window), map);

    gtk_widget_show(map);
    gtk_widget_show(window);
  
    gtk_main();

    return 0;
}
