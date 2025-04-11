import mapnik
from flask import Flask, send_file, Response
import os


app = Flask(__name__)


# Route to generate map from XML
@app.route('/map_from_xml')
def generate_map_from_xml():
    # see the doc for : https://get-map.org/mapnik-lost-manual/book.html
    # create a mapnik map object
    m = mapnik.Map(800, 600)
    # load the mapnik XML file
    mapnik.load_map(m, '/app/map.xml')
    # define the map view
    m.zoom_to_box(mapnik.Box2d(1515091, -202540, 1720540, -102263))
    # m.zoom_all() # use this for the whole map

    # render the map to an image
    # output = '/tmp/map.png'
    # mapnik.render_to_file(m, output, 'png')
    # return the image as a response
    # return send_file(output, mimetype='image/png')

    # render the map to an image in memory
    im = mapnik.Image(m.width,m.height)
    # render the map
    mapnik.render(m, im)
    # serialize the image to PNG format
    img_bytes = im.tostring('png') 
    # return the image as a response
    return Response(img_bytes, mimetype='image/png')

# Route to generate map from Python
@app.route('/map_from_python')
def generate_map_from_python():
    
    # warning mapnik website says it is better to use the xml file
    # in python there is some limitations with the styling

    # create a mapnik map object
    m = mapnik.Map(800,600,"+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs")

    # Set its background colour. More on colours later ...
    m.background = mapnik.Color('white') 

    provpoly_lyr = mapnik.Layer('Provinces')
    provpoly_lyr.srs = "+proj=lcc +ellps=GRS80 +lat_0=49 +lon_0=-95 +lat+1=49 +lat_2=77 +datum=NAD83 +units=m +no_defs"
    provpoly_lyr.datasource = mapnik.Shapefile(file='/data/boundaries')
    
    # define a style for the provinces
    provpoly_style = mapnik.Style()

    # define a rule for the provinces
    provpoly_rule_on = mapnik.Rule()

    # for ontario, we want to use a different colour
    provpoly_rule_on.filter = mapnik.Expression("[NAME_EN] = 'Ontario'")

    sym = mapnik.PolygonSymbolizer()
    sym.fill = mapnik.Color(250, 190, 183)
    
    provpoly_rule_on.symbols.append(sym)
    provpoly_style.rules.append(provpoly_rule_on)

    # for quebec, we want to use a different colour
    provpoly_rule_qc = mapnik.Rule()
    provpoly_rule_qc.filter = mapnik.Expression("[NAME_EN] = 'Quebec'")
    sym = mapnik.PolygonSymbolizer()
    sym.fill = mapnik.Color(217, 235, 203)
    provpoly_rule_qc.symbols.append(sym)
    provpoly_style.rules.append(provpoly_rule_qc)

    # add the style to the map
    m.append_style('provinces', provpoly_style)

    # associate the style with the layer
    provpoly_lyr.styles.append('provinces')

    # add the layer to the map
    m.layers.append(provpoly_lyr)

    # Provincial boundaries

    provlines_lyr = mapnik.Layer('Provincial borders')
    provlines_lyr.srs = "+proj=lcc +ellps=GRS80 +lat_0=49 +lon_0=-95 +lat+1=49 +lat_2=77 +datum=NAD83 +units=m +no_defs"
    provlines_lyr.datasource = mapnik.Shapefile(file='/data/boundaries_l')

    # define a style for the provincial boundaries
    provlines_style = mapnik.Style()
    provlines_rule = mapnik.Rule()
    sym = mapnik.LineSymbolizer()
    
    sym.stroke = mapnik.Color('black')
    #stroke = mapnik.Stroke(mapnik.Color('black'), 1)
    #stroke.add_dash(2, 2)  # Dashed line
    #sym.stroke = stroke
    sym.stroke_width = 1
    sym.stroke_opacity = 1.0
    #sym.stroke_dasharray = "8 4 2 2 2 2"  # Dashed line
    #sym.stroke_dasharray = [6.,2.]  # Dashed line
    provlines_rule.symbols.append(sym)
    provlines_style.rules.append(provlines_rule)

    m.append_style('provlines', provlines_style)
    provlines_lyr.styles.append('provlines')
    m.layers.append(provlines_lyr)

    # Drainage

    # A simple example ...

    # quebec hydrography
    qcdrain_lyr = mapnik.Layer('Quebec Hydrography')
    qcdrain_lyr.srs = "+proj=lcc +ellps=GRS80 +lat_0=49 +lon_0=-95 +lat+1=49 +lat_2=77 +datum=NAD83 +units=m +no_defs"
    qcdrain_lyr.datasource = mapnik.Shapefile(file='/data/qcdrainage')

    # style
    qcdrain_style = mapnik.Style()
    qcdrain_rule = mapnik.Rule()
    qcdrain_rule.filter = mapnik.Expression('[HYC] = 8')
    sym = mapnik.PolygonSymbolizer()
    sym.fill = mapnik.Color(153, 204, 255, 255)
    sym.smooth = 1.0 # very smooth
    qcdrain_rule.symbols.append(sym)
    qcdrain_style.rules.append(qcdrain_rule)

    m.append_style('drainage', qcdrain_style)
    qcdrain_lyr.styles.append('drainage')
    m.layers.append(qcdrain_lyr)

    # Ontario hydrography
    ondrain_lyr = mapnik.Layer('Ontario Hydrography')
    ondrain_lyr.srs = "+proj=lcc +ellps=GRS80 +lat_0=49 +lon_0=-95 +lat+1=49 +lat_2=77 +datum=NAD83 +units=m +no_defs"
    ondrain_lyr.datasource = mapnik.Shapefile(file='/data/ontdrainage')

    ondrain_lyr.styles.append('drainage')
    m.layers.append(ondrain_lyr)
   
    # Roads layer - class 3 and 4 (The "grey" roads)
    
    roads34_lyr = mapnik.Layer('Roads')
    roads34_lyr.srs = "+proj=lcc +ellps=GRS80 +lat_0=49 +lon_0=-95 +lat+1=49 +lat_2=77 +datum=NAD83 +units=m +no_defs"
    
    roads34_lyr.datasource = mapnik.Shapefile(file='/data/roads')

    roads34_style = mapnik.Style()
    roads34_rule = mapnik.Rule()
    roads34_rule.filter = mapnik.Expression('([CLASS] = 3) or ([CLASS] = 4)')

    # small road style
    sym = mapnik.LineSymbolizer()
    sym.stroke = mapnik.Color(171,158,137)
    sym.stroke_width = 2
    sym.stroke_linecap = mapnik.stroke_linecap.ROUND_CAP

    roads34_rule.symbols.append(sym)
    roads34_style.rules.append(roads34_rule)

    m.append_style('smallroads', roads34_style)
    roads34_lyr.styles.append('smallroads')
    m.layers.append(roads34_lyr)

    # Roads 2 (The thin yellow ones)
    roads2_lyr = mapnik.Layer('Roads')
    roads2_lyr.srs = "+proj=lcc +ellps=GRS80 +lat_0=49 +lon_0=-95 +lat+1=49 +lat_2=77 +datum=NAD83 +units=m +no_defs"
    # Just get a copy from roads34_lyr
    roads2_lyr.datasource = roads34_lyr.datasource

    # style for roads 2
    # 2 symbolizers, one for the border and one for the fill
    roads2_style_1 = mapnik.Style()
    roads2_rule_1 = mapnik.Rule()
    roads2_rule_1.filter = mapnik.Expression('[CLASS] = 2')

    sym = mapnik.LineSymbolizer()
    sym.stroke = mapnik.Color(171,158,137)
    sym.stroke_width = 4
    sym.stroke_linecap = mapnik.stroke_linecap.ROUND_CAP
    roads2_rule_1.symbols.append(sym)
    roads2_style_1.rules.append(roads2_rule_1)

    m.append_style('road-border', roads2_style_1)

    roads2_style_2 = mapnik.Style()
    roads2_rule_2 = mapnik.Rule()
    roads2_rule_2.filter = mapnik.Expression('[CLASS] = 2')
    sym = mapnik.LineSymbolizer()
    sym.stroke = mapnik.Color(255,250,115)
    sym.stroke_linecap = mapnik.stroke_linecap.ROUND_CAP
    sym.stroke_width = 2
    roads2_rule_2.symbols.append(sym)
    roads2_style_2.rules.append(roads2_rule_2)

    m.append_style('road-fill', roads2_style_2)

    roads2_lyr.styles.append('road-border')
    roads2_lyr.styles.append('road-fill')

    m.layers.append(roads2_lyr)

    # Roads 1 (The big orange ones, the highways)
    roads1_lyr = mapnik.Layer('Roads')
    roads1_lyr.srs = "+proj=lcc +ellps=GRS80 +lat_0=49 +lon_0=-95 +lat+1=49 +lat_2=77 +datum=NAD83 +units=m +no_defs"
    roads1_lyr.datasource = roads34_lyr.datasource

    # style for highways
    # 2 symbolizers, one for the border and one for the fill
    roads1_style_1 = mapnik.Style()
    roads1_rule_1 = mapnik.Rule()
    roads1_rule_1.filter = mapnik.Expression('[CLASS] = 1')
    sym = mapnik.LineSymbolizer()
    sym.stroke = mapnik.Color(188,149,28)
    sym.stroke_linecap = mapnik.stroke_linecap.ROUND_CAP
    sym.stroke_width = 7
    roads1_rule_1.symbols.append(sym)
    roads1_style_1.rules.append(roads1_rule_1)
    m.append_style('highway-border', roads1_style_1)

    roads1_style_2 = mapnik.Style()
    roads1_rule_2 = mapnik.Rule()
    roads1_rule_2.filter = mapnik.Expression('[CLASS] = 1')
    sym.stroke = mapnik.Color(242,191,36)
    sym.stroke_linecap = mapnik.stroke_linecap.ROUND_CAP
    sym.stroke_width = 5
    roads1_rule_2.symbols.append(sym)
    roads1_style_2.rules.append(roads1_rule_2)

    m.append_style('highway-fill', roads1_style_2)

    roads1_lyr.styles.append('highway-border')
    roads1_lyr.styles.append('highway-fill')

    m.layers.append(roads1_lyr)

    # Populated Places
    popplaces_lyr = mapnik.Layer('Populated Places')
    popplaces_lyr.srs = "+proj=lcc +ellps=GRS80 +lat_0=49 +lon_0=-95 +lat+1=49 +lat_2=77 +datum=NAD83 +units=m +no_defs"
    popplaces_lyr.datasource = mapnik.Shapefile(file='/data/popplaces')

    popplaces_style = mapnik.Style()
    popplaces_rule = mapnik.Rule()

    # # And here we have a TextSymbolizer, used for labeling.
    # # The first parameter is the name of the attribute to use as the source of the
    # # text to label with.  Then there is font size in points (I think?), and colour.

    # # TODO - currently broken: https://github.com/mapnik/mapnik/issues/2324

    # popplaces_text_sym = mapnik.TextSymbolizer()
    # popplaces_text_sym.fill = mapnik.Color('black')
    # #popplaces_text_sym.face_name  = 'DejaVu Sans Book'
    # #popplaces_text_sym.size = 10
    # #popplaces_text_sym.halo_fill = mapnik.Color(255,255,200)
    # popplaces_text_sym.halo_radius = 1.0
    # popplaces_text_sym.allow_overlap = True
    # popplaces_text_sym.label_placement = mapnik.label_placement.POINT_PLACEMENT
    # popplaces_text_sym.minimum_padding = 30
    # popplaces_text_sym.allow_overlap = True
    # popplaces_text_sym.avoid_edges = True
    # popplaces_text_sym.label_placement = mapnik.label_placement.POINT_PLACEMENT
    # popplaces_text_sym.minimum_padding = 30
    # popplaces_text_sym.allow_overlap = True
    # popplaces_text_sym.placement_finder = mapnik.PlacementFinder()
    # popplaces_text_sym.placement_finder.face_name = 'DejaVu Sans Book'
    # popplaces_text_sym.placement_finder.text_size = 10
    # popplaces_text_sym.placement_finder.halo_fill = mapnik.Color(255,255,200)
    # popplaces_text_sym.placement_finder.halo_radius = 1.0
    # popplaces_text_sym.placement_finder.fill = "black"
    # popplaces_text_sym.placement_finder.format_expression = "[GEONAME]"


    # # We set a "halo" around the text, which looks like an outline if thin enough,
    # # or an outright background if large enough.
    # #popplaces_text_sym.label_placement= mapnik.label_placement.POINT_PLACEMENT
    # #popplaces_text_sym.halo_fill = mapnik.Color(255,255,200)
    # #popplaces_text_sym.halo_radius = 1
    # #popplaces_text_sym.avoid_edges = True
    # #popplaces_text_sym.minimum_padding = 30

    # popplaces_rule.symbols.append(popplaces_text_sym)

    # popplaces_style.rules.append(popplaces_rule)

    # m.append_style('popplaces', popplaces_style)
    # popplaces_lyr.styles.append('popplaces')
    # m.layers.append(popplaces_lyr)

    # Draw map

    # Set the initial extent of the map in 'master' spherical Mercator projection
    m.zoom_to_box(mapnik.Box2d(-8024477.28459,5445190.38849,-7381388.20071,5662941.44855))

    # Render map
    im = mapnik.Image(m.width,m.height)
    mapnik.render(m, im)

    # Save the map to a file
    # output = '/tmp/map2.png'
    # mapnik.render_to_file(m, output, 'png')

    # return send_file(output, mimetype='image/png')
    img_bytes = im.tostring('png')  # Sérialiser en format PNG

    # return the image as a response
    return Response(img_bytes, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)