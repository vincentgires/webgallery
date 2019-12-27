dt = require 'darktable'

local DEFAULT_RATING = 3

local function get_tags(args)
  args.rating = args.rating or DEFAULT_RATING
  -- args.exclude_words = args.exclude_words or {'darktable'} -- remove default darktable tags
  local result = {}
  for _, img in ipairs(dt.database) do
    if img.rating >= args.rating then
      local tags = dt.tags.get_tags(img)
      local img_tags = {}
      for _, tag in ipairs(tags) do
        tag = tostring(tag)
        if not string.find(tag, 'darktable') then -- TODO: make it an option
          table.insert(img_tags, tag)
        end
      end
      if #img_tags >= 1 then
        result[img.filename] = img_tags
      end
    end
  end
  return result
end

local function table_length(t)
  local count = 0
  for _ in pairs(t) do count = count + 1 end
  return count
end

local function build_json_tags()
  local generated_tags = get_tags{}
  local count = 1
  local result = '{'
  for img, tags in pairs(generated_tags) do
    result = result..'"'..img..'"'..':['
    for i, tag in ipairs(tags) do
      result = result..'"'..tag..'"'
      if i < #tags then
        result = result..','
      else
        result = result..']'
        if count < table_length(generated_tags) then
          result = result..','
        end
      end
    end
    count = count + 1
  end
  return result..'}'
end

local function export_tags_as_json(path)
  local json_tags = build_json_tags()
  local file = io.open(path, 'w+')
  file:write(json_tags)
  file:close()
  print(json_tags)
  print('json exported to '..path)
end

local export_path = dt.new_widget('entry') {
  tooltip = 'target path to export file',
  text = '/home/'..os.getenv('USER')..'/tags.json',
  reset_callback = function(self) self.text = '' end
}

local export_btn = dt.new_widget('button') {
  tooltip = 'export tags to json',
  label = 'export to json',
  clicked_callback = function(self) export_tags_as_json(export_path.text) end
}
local webgallery_widget = dt.new_widget('box'){
  orientation = 'vertical',
  export_path,
  export_btn
}

dt.register_lib('export_tags', 'export tags', true, true, {
  [dt.gui.views.lighttable] = {'DT_UI_CONTAINER_PANEL_LEFT_CENTER', 20},
}, webgallery_widget)
