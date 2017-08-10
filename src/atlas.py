import common
import image
import hash
import array

static class LandAtlasSprite:
    int x, y, w, h, ox, oy
    LandAtlasSheet *sheet

static class LandAtlasSheet:
    char *filename
    int id
    LandImage *image

class LandAtlas:
    LandArray *sheets # LandAtlasSheet
    LandHash *sprites # LandAtlasSprite
    char *filename

def land_atlas_new(char const *filename) -> LandAtlas*:
    LandAtlas *self
    land_alloc(self)
    self.sheets = land_array_new()
    self.sprites = land_hash_new()
    self.filename = land_strdup(filename)

    land_atlas_load_all(self)
    return self

def land_atlas_destroy(LandAtlas *self):
    for LandAtlasSheet *sheet in LandArray *self.sheets:
        land_image_destroy(sheet.image)
        land_free(sheet.filename)
        land_free(sheet)
    for LandAtlasSprite *s in LandHash *self.sprites:
        land_free(s)
    land_array_destroy(self.sheets)
    land_hash_destroy(self.sprites)
    land_free(self.filename)
    land_free(self)

static def atlas_find_sheet(LandAtlas *self, char const *name) -> LandAtlasSheet*:
    for LandAtlasSheet *sheet in LandArray *self.sheets:
        if land_equals(name, sheet.filename):
            return sheet
    return None

def land_atlas_load_all(LandAtlas *self):
    char *text = land_read_text(self.filename)
    LandArray *a = land_split_lines(text)

    for char *row in LandArray *a:
        char *path = row
        char *colon = strchr(path, ':')
        if not colon:
            break
        *colon = '\0'
        char *sheet = colon + 2
        char *space = strchr(sheet, ' ')
        *space = '\0'
        LandAtlasSprite *s
        land_alloc(s)
        LandAtlasSheet *atlas_sheet = atlas_find_sheet(self, sheet)
        if not atlas_sheet:
            land_alloc(atlas_sheet)
            atlas_sheet.filename = land_strdup(sheet)
            atlas_sheet.id = land_array_count(self.sheets)
            land_array_add(self.sheets, atlas_sheet)
            char *sheet_path = land_replace_filename(self.filename, sheet)
            atlas_sheet.image = land_image_load(sheet_path)
            land_free(sheet_path)
        s.sheet = atlas_sheet
        sscanf(space + 1, " %d %d %d %d %d %d\n",
            &s.x, &s.y, &s.w, &s.h, &s.ox, &s.oy)
        land_hash_insert(self.sprites, path, s)
    
    land_free(text)
    land_array_destroy_with_strings(a)

static def atlas_load_picture(LandAtlas *self, char const *filename) -> LandAtlasSprite *:
    return land_hash_get(self.sprites, filename)
    
def land_atlas_image_create(LandAtlas *self, char const *filename) -> LandImage*:
    LandAtlasSprite *sprite = atlas_load_picture(self, filename)
    if not sprite: return None
    LandImage *image = land_image_sub(sprite.sheet.image, sprite.x, sprite.y,
        sprite.w, sprite.h)
    land_image_offset(image, -sprite.ox, -sprite.oy)
    return image
    
