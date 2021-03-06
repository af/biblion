from django.contrib import admin
from django.utils.functional import curry

from biblion.models import Post, Image
from biblion.forms import AdminPostForm
from biblion.utils import can_tweet


class ImageInline(admin.TabularInline):
    model = Image
    fields = ["image_path"]


class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "published_flag", "section", "author", "created", "published",]
    list_filter = ["section"]
    raw_id_fields = ('author',)
    form = AdminPostForm
    prepopulated_fields = {"slug": ("title",)}
    inlines = [
        ImageInline,
    ]
    fieldsets = (
        (None, {
            "fields": ("section", "title", "slug", "author", "content", "publish",)
        }),
        ("Optional", {
            "classes": ("collapse",),
            "fields": ("teaser",)
        }),
    )
    if can_tweet():
        fieldsets[0][1]['fields'].append("tweet")
    
    def published_flag(self, obj):
        return bool(obj.published)
    published_flag.short_description = "Published"
    published_flag.boolean = True
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs.pop("request")
        if db_field.name == "author":
            ff = super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            ff.initial = request.user.id
            return ff
        return super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        kwargs.update({
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
        })
        return super(PostAdmin, self).get_form(request, obj, **kwargs)
    
    def save_form(self, request, form, change):
        # this is done for explicitness that we want form.save to commit
        # form.save doesn't take a commit kwarg for this reason
        return form.save()


admin.site.register(Post, PostAdmin)
admin.site.register(Image)
