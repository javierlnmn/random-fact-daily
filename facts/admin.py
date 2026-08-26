from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Fact, Reaction, FactStatus

status_color = {
    FactStatus.VISITED: {
        "color": "#41d97b",
        "background-color": "rgba(65, 217, 123, 0.2)",
    },
    FactStatus.CURRENT: {
        "color": "#417bd9",
        "background-color": "rgba(65, 123, 217, 0.2)",
    },
    FactStatus.NOT_VISITED: {
        "color": "#d94164",
        "background-color": "rgba(217, 65, 100, 0.2)",
    },
}


@admin.register(Fact)
class FactAdmin(admin.ModelAdmin):
    list_display = ("fact", "status_display", "identifier", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("fact", "identifier", "description")
    list_display_links = ("fact", "identifier")
    prepopulated_fields = {"identifier": ("fact",)}

    def status_display(self, obj):
        status = FactStatus(obj.status)
        return format_html(
            f"""<span
                    style='
                        display: inline-block;
                        color: {status_color[status]["color"]};
                        background-color: {status_color[status]["background-color"]};
                        padding: 2px 4px;
                        border-radius: 50px;
                        min-width: 100px;
                        text-align: center;
                    '>
                    {status.label}
                </span>
            """,
        )

    status_display.allow_tags = True
    status_display.admin_order_field = "status"
    status_display.short_description = "status"


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("fact", "reaction", "session_id", "user")
    list_filter = ("fact", "reaction", "session_id", "user")
    search_fields = ("fact", "reaction", "session_id", "user")
    list_display_links = ("fact", "reaction")


admin.site.register(Category)
