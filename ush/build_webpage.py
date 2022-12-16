'''
Program Name: build_webpage.py
Contact(s): Mallory Row
Abstract: This is run at the end of all step2 scripts
          in scripts/.
          This creates a job card to:
              1) if needed, create website from
                 EMC_verif-global template (webpage.tar)
                 at specified user location on web server
              2) send images to web server
          It then submits to the transfer queue.
'''

import os
import datetime
import glob
import shutil
from functools import partial

print = partial(print, flush=True)

print("BEGIN: "+os.path.basename(__file__))

# Read in environment variables
KEEPDATA = os.environ['KEEPDATA']
machine = os.environ['machine']
USHverif_global = os.environ['USHverif_global']
DATA = os.environ['DATA']
NET = os.environ['NET']
RUN = os.environ['RUN']
RUN_type = RUN.split('_')[0]
QUEUESERV = os.environ['QUEUESERV']
ACCOUNT = os.environ['ACCOUNT']
PARTITION_BATCH = os.environ['PARTITION_BATCH']
webhost = os.environ['webhost']
webhostid = os.environ['webhostid']
webdir = os.environ['webdir']
print("Webhost: "+webhost)
if RUN == 'fit2obs_plots':
    DATA = DATA.replace('/fit2obs_plots/data', '')
    webdir = webdir.replace(
        '/fits/horiz/'+os.environ['fit2obs_plots_expnlist'].split(' ')[1], ''
    )
    web_fits_dir = os.path.join(DATA, RUN, 'fit2obs', 'web', 'fits')
    nimages = 0
    for root, dirs, files in os.walk(web_fits_dir, topdown=False):
        nimages = nimages + len(glob.glob(os.path.join(root, '*.png')))
    print("Webhost location: "+webdir)
    print("\nTotal images within "+web_fits_dir+": "+str(nimages))
else:
    image_list = os.listdir(
        os.path.join(DATA, RUN, 'metplus_output', 'images')
    )
    nimages = len(image_list)
    print("Webhost location: "+webdir)
    print("\nTotal images in "
          +os.path.join(DATA, RUN, 'metplus_output', 'images')+": "
          +str(nimages))

# Set up job wall time information
web_walltime = '180'
walltime_seconds = datetime.timedelta(minutes=int(web_walltime)) \
        .total_seconds()
walltime = (datetime.datetime.min
           + datetime.timedelta(minutes=int(web_walltime))).time()

# Create webpage templates for tropcyc
def tropcyc_write_template_header(template_filename):
    """! Writes common webpage header information to
         template

         Args:
             template_filename - string of the full
                                 file path to write to

         Returns:
    """
    template_type = template_filename.split('/')[-1].split('_')[0]
    template_file = open(template_filename, 'w')
    template_file.write(
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
        +'"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
    )
    template_file.write(
        '<html xmlns="http://www.w3.org/1999/xhtml" '
        +'xml:lang="en" lang="en">\n'
    )
    template_file.write('\n')
    template_file.write('<head>\n')
    template_file.write(
        '<meta http-equiv="content-type" content="text/html; '
        +'charset=utf-8" />\n'
    )
    template_file.write('<title>Home</title>\n')
    template_file.write(
        '<link href="../../main.css" rel="stylesheet" type="text/css" '
        +'media="all" />\n'
    )
    template_file.write(
        '<link href="../../fonts.css" rel="stylesheet" type="text/css" '
        +'media="all" />\n'
    )
    template_file.write(
        '<script src="https://d3js.org/d3.v4.min.js"></script>\n'
    )
    template_file.write(
        '<script src="../jquery-3.1.1.min.js"></script>\n'
    )
    template_file.write(
        '<script type="text/javascript" '
        +'src="../functions_metplus.js"></script>\n'
    )
    template_file.write(
        '<meta name="viewport" content="width=device-width, '
        +'initial-scale=1.0">\n'
    )
    template_file.write('</head>\n')
    template_file.write('\n')
    template_file.write('<?php\n')
    template_file.write(
        '$randomtoken = base64_encode( openssl_random_pseudo_bytes(32));\n'
    )
    template_file.write(
        "$_SESSION['csrfToken']=$randomtoken;\n"
    )
    template_file.write('?>\n')
    template_file.write('\n')
    template_file.write(
        '<?php include "'+template_type+'_globalvars.php"; ?>\n'
    )
    template_file.write('\n')
    template_file.close()

def tropcyc_write_template_body1(template_filename):
    """! Writes common webpage body information to
         template before the javascript domain
         assignment portion

         Args:
             template_filename - string of the full
                                 file path to write to

         Returns:
    """
    template_type = template_filename.split('/')[-1].split('_')[0]
    template_file = open(template_filename, 'a')
    template_file.write('<body>\n')
    template_file.write('<div id="pageTitle">\n')
    template_file.write('<?php echo $stat_title; ?>\n')
    template_file.write('</div>\n')
    template_file.write('<div class="page-menu"><div class="table">\n')
    template_file.write('        <div class="element">\n')
    template_file.write('                <span class="bold">Basin:</span>\n')
    template_file.write(
        '                <select id="maptype" '
        +'onchange="changeMaptype(this.value)"></select>\n'
    )
    template_file.write('        </div>\n')
    template_file.write('        <div class="element">\n')
    template_file.write('                <span class="bold">Name:</span>\n')
    template_file.write(
        '                <select id="domain" '
        +'onchange="changeDomain(this.value);"></select>\n'
    )
    template_file.write('        </div>\n')
    template_file.write('        <div class="element">\n')
    template_file.write(
        '                <span class="bold">Forecast Lead:</span>\n'
    )
    template_file.write(
        '                <select id="variable" '
        +'onchange="changeVariable(this.value)"></select>\n'
    )
    template_file.write('        </div>\n')
    template_file.write('</div></div>\n')
    template_file.write('\n')
    template_file.write('<!-- Middle menu -->\n')
    template_file.write('<div class="page-middle" id="page-middle">\n')
    template_file.write(
        'Left/Right arrow keys = Change forecast lead | Up/Down arrow keys '
        +'= Change Storm\n'
    )
    template_file.write(
        '<br>For information on tropical cyclone verification, '
        +'<button class="infobutton" id="myBtn">click here</button>\n'
    )
    template_file.write('<div id="myModal" class="modal">\n')
    template_file.write('  <div class="modal-content">\n')
    template_file.write('    <span class="close">&times;</span>\n')
    template_file.write('    Tropical Cyclone Verification Information\n')
    template_file.write(
        '    <iframe width=100% height=90% src="../main.php" '
        +'style="border:none;"></iframe>\n'
    )
    template_file.write('  </div>\n')
    template_file.write('</div>\n')
    template_file.write('<!-- /Middle menu -->\n')
    template_file.write('</div>\n')
    template_file.write('\n')
    template_file.write(
        '<div id="loading"><img style="width:100%" '
        +'src="../../images/loading.png"></div>\n'
    )
    template_file.write('\n')
    template_file.write('<!-- Image -->\n')
    template_file.write('<div id="page-map">\n')
    template_file.write('        <image name="map" style="width:100%">\n')
    template_file.write('</div>\n')
    template_file.write('\n')
    template_file.write('<script type="text/javascript">\n')
    template_file.write('// Get the modal\n')
    template_file.write('var modal = document.getElementById("myModal");\n')
    template_file.write('\n')
    template_file.write('// Get the button that opens the modal\n')
    template_file.write('var btn = document.getElementById("myBtn");\n')
    template_file.write('\n')
    template_file.write('// Get the <span> element that closes the modal\n')
    template_file.write(
        'var span = document.getElementsByClassName("close")[0];\n'
    )
    template_file.write('\n')
    template_file.write(
        '// When the user clicks the button, open the modal\n'
    )
    template_file.write('btn.onclick = function() {\n')
    template_file.write('  modal.style.display = "block";\n')
    template_file.write('}\n')
    template_file.write('\n')
    template_file.write(
        '// When the user clicks on <span> (x), close the modal\n'
    )
    template_file.write('span.onclick = function() {\n')
    template_file.write('  modal.style.display = "none";\n')
    template_file.write('}\n')
    template_file.write('\n')
    template_file.write(
        '// When the user clicks anywhere outside of the modal, close it\n'
    )
    template_file.write('window.onclick = function(event) {\n')
    template_file.write('  if (event.target == modal) {\n')
    template_file.write('    modal.style.display = "none";\n')
    template_file.write('  }\n')
    template_file.write('}\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('//User-defined variables\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('\n')
    template_file.write('//Global variables\n')
    template_file.write(
        'var minFrame = 0; //Minimum frame for every variable\n'
    )
    template_file.write(
        'var maxFrame = 26; //Maximum frame for every variable\n'
    )
    template_file.write(
        'var incrementFrame = 1; //Increment for every frame\n'
    )
    template_file.write('\n')
    template_file.write('var startFrame = 0; //Starting frame\n')
    template_file.write('\n')
    template_file.write('var cycle = 2018100600\n')
    template_file.write('\n')
    template_file.write('/*\n')
    template_file.write(
        'When constructing the URL below, DDD = domain, VVV = variable, '
        +'LLL = level, SSS = season, Y = frame number.\n'
    )
    template_file.write(
        'For X and Y, labeling one X or Y represents an integer '
        +'(e.g. 0, 10, 20). Multiple of these represent a string\n'
    )
    template_file.write(
        'format (e.g. XX = 00, 06, 12 --- XXX = 000, 006, 012).\n'
    )
    template_file.write('*/\n')
    template_file.write(
        'var url = "<?php echo $'+template_type+'_url; ?>";\n'
    )
    template_file.write('\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('//Add variables & domains\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('\n')
    template_file.write('var variables = [];\n')
    template_file.write('var domains = [];\n')
    template_file.write('var levels = [];\n')
    template_file.write('var seasons = [];\n')
    template_file.write('var maptypes = [];\n')
    template_file.write('var validtimes = [];\n')
    template_file.write('\n')
    template_file.write('\n')
    template_file.close()

def tropcyc_write_template_body2(template_filename):
    """! Writes common webpage body information to
         template after the javascript domain
         assignment portion

         Args:
             template_filename - string of the full
                                 file path to write to

         Returns:
    """
    template_type = template_filename.split('/')[-1].split('_')[0]
    basin = template_filename.split('/')[-1].split('_')[1].replace('.php', '')
    template_file = open(template_filename, 'a')
    template_file.write('domains.push({\n')
    template_file.write('        displayName: "All",\n')
    template_file.write('        name: "'+basin+'",\n')
    template_file.write('});\n')
    template_file.write('\n')
    template_file.write('\n')
    template_file.write('variables.push({\n')
    template_file.write('        displayName: "Mean",\n')
    template_file.write('        name: "<?php echo $LeadMean_name; ?>",\n')
    template_file.write('});\n')
    template_file.write('\n')
    template_file.write('\n')
    template_file.write('maptypes.push({\n')
    template_file.write('        url: "'+template_type+'_AL.php",\n')
    template_file.write('        displayName: "Atlantic",\n')
    template_file.write('        name: "'+template_type+'_AL",\n')
    template_file.write('});\n')
    template_file.write('maptypes.push({\n')
    template_file.write('        url: "'+template_type+'_CP.php",\n')
    template_file.write('        displayName: "Central Pacific",\n')
    template_file.write('        name: "'+template_type+'_CP",\n')
    template_file.write('});\n')
    template_file.write('maptypes.push({\n')
    template_file.write('        url: "'+template_type+'_EP.php",\n')
    template_file.write('        displayName: "Eastern Pacific",\n')
    template_file.write('        name: "'+template_type+'_EP",\n')
    template_file.write('});\n')
    template_file.write('maptypes.push({\n')
    template_file.write('        url: "'+template_type+'_WP.php",\n')
    template_file.write('        displayName: "Western Pacific",\n')
    template_file.write('        name: "'+template_type+'_WP",\n')
    template_file.write('});\n')
    template_file.write('\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('//Initialize the page\n')
    template_file.write(
        '//======================================================='
        +'=============================================\n'
    )
    template_file.write('//function for keyboard controls\n')
    template_file.write('document.onkeydown = keys;\n')
    template_file.write('\n')
    template_file.write(
        '//Decare object containing data about the currently displayed map\n'
    )
    template_file.write('imageObj = {};\n')
    template_file.write('\n')
    template_file.write('//Initialize the page\n')
    template_file.write('initialize();\n')
    template_file.write('\n')
    template_file.write(
        '//Format initialized run date & return in requested format\n'
    )
    template_file.write('function formatDate(offset,format){\n')
    template_file.write('        var newdate = String(cycle);\n')
    template_file.write('        var yyyy = newdate.slice(0,4)\n')
    template_file.write('        var mm = newdate.slice(4,6);\n')
    template_file.write('        var dd = newdate.slice(6,8);\n')
    template_file.write('        var hh = newdate.slice(8,10);\n')
    template_file.write(
        '        var curdate = new Date(yyyy,parseInt(mm)-1,dd,hh)\n'
    )
    template_file.write('\n')
    template_file.write('\n')
    template_file.write('        //Offset by run\n')
    template_file.write(
        '        var newOffset = curdate.getHours() + offset;\n'
    )
    template_file.write('        curdate.setHours(newOffset);\n')
    template_file.write('\n')
    template_file.write(
        '        var yy = String(curdate.getFullYear()).slice(2,4);\n'
    )
    template_file.write('        yyyy = curdate.getFullYear();\n')
    template_file.write('        mm = curdate.getMonth()+1;\n')
    template_file.write('        dd = curdate.getDate();\n')
    template_file.write('        if(dd < 10){dd = "0" + dd;}\n')
    template_file.write('        hh = curdate.getHours();\n')
    template_file.write('        if(hh < 10){hh = "0" + hh;}\n')
    template_file.write('\n')
    template_file.write('        var wkday = curdate.getDay();\n')
    template_file.write(
        '        var day_str = ["Sun", "Mon", "Tue", "Wed", '
        +'"Thu", "Fri", "Sat"];\n'
    )
    template_file.write('\n')
    template_file.write('        //Return in requested format\n')
    template_file.write("        if(format == 'valid'){\n")
    template_file.write('//06Z Thu 03/22/18 (90 h)\n')
    template_file.write(
        'var txt = hh + "Z " + day_str[wkday] + " " + '
        +'mm + "/" + dd + "/" + yy;\n'
    )
    template_file.write('                return txt;\n')
    template_file.write('        }\n')
    template_file.write('}\n')
    template_file.write('\n')
    template_file.write('//Initialize the page\n')
    template_file.write('function initialize(){\n')
    template_file.write('\n')
    template_file.write(
        '        //Set image object based on default variables\n'
    )
    template_file.write('        imageObj = {\n')
    template_file.write(
       '                variable: "<?php echo $LeadMean_name; ?>",\n'
    )
    template_file.write('                domain: "'+basin+'"\n')
    template_file.write('        };\n')
    template_file.write('\n')
    template_file.write(
        '        //Change domain based on passed argument, if any\n'
    )
    template_file.write('        var passed_domain = "";\n')
    template_file.write('        if(passed_domain!=""){\n')
    template_file.write(
        '                if(searchByName(passed_domain,domains)>=0){\n'
    )
    template_file.write(
        '                        imageObj.domain = passed_domain;\n'
    )
    template_file.write('                }\n')
    template_file.write('        }\n')
    template_file.write('\n')
    template_file.write(
        '        //Change variable based on passed argument, if any\n'
    )
    template_file.write('        var passed_variable = "";\n')
    template_file.write('        if(passed_variable!=""){\n')
    template_file.write(
        '                if(searchByName(passed_variable,variables)>=0){\n'
    )
    template_file.write(
        '                        imageObj.variable = passed_variable;\n'
    )
    template_file.write('                }\n')
    template_file.write('        }\n')
    template_file.write('\n')
    template_file.write(
        '        //Populate forecast hour and dprog/dt arrays for this '
        +'run and frame\n'
    )
    template_file.write("        populateMenu('variable');\n")
    template_file.write("        populateMenu('domain');\n")
    template_file.write("        populateMenu('maptype')\n")
    template_file.write('\n')
    template_file.write('        //Populate the frames arrays\n')
    template_file.write('        frames = [];\n')
    template_file.write(
        '        for(i=minFrame;i<=maxFrame;i=i+incrementFrame)'
        +'{frames.push(i);}\n'
    )
    template_file.write('\n')
    template_file.write(
        '        //Predefine empty array for preloading images\n'
    )
    template_file.write('        for(i=0; i<variables.length; i++){\n')
    template_file.write('                variables[i].images = [];\n')
    template_file.write('                variables[i].loaded = [];\n')
    template_file.write('                variables[i].dprog = [];\n')
    template_file.write('        }\n')
    template_file.write('\n')
    template_file.write('        //Preload images and display map\n')
    template_file.write('        preload(imageObj);\n')
    template_file.write('        showImage();\n')
    template_file.write('\n')
    template_file.write('        //Update mobile display for swiping\n')
    template_file.write('        updateMobile();\n')
    template_file.write('\n')
    template_file.write('}\n')
    template_file.write('\n')
    template_file.write('var xInit = null;\n')
    template_file.write('var yInit = null;\n')
    template_file.write('var xPos = null;\n')
    template_file.write('var yPos = null;\n')
    template_file.write('\n')
    template_file.write('</script>\n')
    template_file.write('\n')
    template_file.write('</body>\n')
    template_file.write('</html>\n')
    template_file.close()

if RUN == 'tropcyc':
    import get_tc_info
    config_storm_list = os.environ['tropcyc_storm_list'].split(' ')
    # Check storm_list to see if all storms for basin and year
    # requested
    tc_dict = get_tc_info.get_tc_dict()
    storm_list = []
    for config_storm in config_storm_list:
        config_storm_basin = config_storm.split('_')[0]
        config_storm_year = config_storm.split('_')[1]
        config_storm_name = config_storm.split('_')[2]
        if config_storm_name == 'ALLNAMED':
            for byn in list(tc_dict.keys()):
                if config_storm_basin+'_'+config_storm_year in byn:
                    storm_list.append(byn)
        else:
            storm_list.append(config_storm)
    # Group storms by basin
    AL_storm_list, CP_storm_list, EP_storm_list, WP_storm_list = [], [], [], []
    for storm in storm_list:
        basin = storm.split('_')[0]
        if basin == 'AL':
            AL_storm_list.append(storm)
        elif basin == 'CP':
            CP_storm_list.append(storm)
        elif basin == 'EP':
            EP_storm_list.append(storm)
        elif basin == 'WP':
            WP_storm_list.append(storm)
    basin_storms_dict = {
        'AL': AL_storm_list,
        'CP': CP_storm_list,
        'EP': EP_storm_list,
        'WP': WP_storm_list
    }
    # Create track and intensity error templates
    trackerr_template_dir = os.path.join(DATA, RUN, 'create_webpage_templates',
                                        'trackerr')
    if not os.path.exists(trackerr_template_dir):
        os.makedirs(trackerr_template_dir)
    intensityerr_template_dir = os.path.join(DATA, RUN,
                                             'create_webpage_templates',
                                             'intensityerr')
    if not os.path.exists(intensityerr_template_dir):
        os.makedirs(intensityerr_template_dir)
    for basin in list(basin_storms_dict.keys()):
        basin_trackerr_filename = os.path.join(trackerr_template_dir,
                                               'trackerr_'+basin+'.php')
        basin_intensityerr_filename = os.path.join(intensityerr_template_dir,
                                                  'intensityerr_'+basin+'.php')
        tropcyc_write_template_header(basin_trackerr_filename)
        tropcyc_write_template_header(basin_intensityerr_filename)
        tropcyc_write_template_body1(basin_trackerr_filename)
        tropcyc_write_template_body1(basin_intensityerr_filename)
        basin_trackerr_file = open(basin_trackerr_filename, 'a')
        basin_intensityerr_file = open(basin_intensityerr_filename, 'a')
        for storm in basin_storms_dict[basin]:
            basin = storm.split('_')[0]
            year = storm.split('_')[1]
            name = storm.split('_')[2]
            basin_trackerr_file.write('domains.push({\n')
            basin_trackerr_file.write(
                '        displayName: "'+name.title()+' ('+year+')",\n'
            )
            basin_trackerr_file.write('        name: "'+storm+'",\n')
            basin_trackerr_file.write('});\n')
            basin_intensityerr_file.write('domains.push({\n')
            basin_intensityerr_file.write(
                '        displayName: "'+name.title()+' ('+year+')",\n'
            )
            basin_intensityerr_file.write('        name: "'+storm+'",\n')
            basin_intensityerr_file.write('});\n')
        basin_trackerr_file.close()
        basin_intensityerr_file.close()
        tropcyc_write_template_body2(basin_trackerr_filename)
        tropcyc_write_template_body2(basin_intensityerr_filename)
elif RUN == 'fit2obs_plots':
    exp1 = os.environ['fit2obs_plots_expnlist'].split(' ')[0]
    exp2 = os.environ['fit2obs_plots_expnlist'].split(' ')[1]
    fit2obs_plots_dir = os.path.join(DATA, RUN)
    # Make globalvars.php files
    for stat in ['bias', 'rmse']:
        stat_globvars_filename = os.path.join(fit2obs_plots_dir,
                                              stat+'_globalvars.php')
        with open(stat_globvars_filename, 'a') as stat_globvars_file:
            stat_globvars_file.write("<?php include '../../globalvars.php';\n")
            if stat == 'rmse':
                stat_globvars_file.write("      $stat_title = 'Fit-to-Obs: "
                                         +stat.upper()+"';\n")
            else:
                stat_globvars_file.write("      $stat_title = 'Fit-to-Obs: "
                                         +stat.title()+"';\n")
            stat_globvars_file.write("      $ADPUPA_url = $image_location.'/"
                                     +stat+"_ADPUPA_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $ADPSFC_url = $image_location.'/"
                                     +stat+"_ADPSFC_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $SFCSHP_url = $image_location.'/"
                                     +stat+"_SFCSHP_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $AIRCFT_url = $image_location.'/"
                                     +stat+"_AIRCFT_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $AIRCAR_url = $image_location.'/"
                                     +stat+"_AIRCAR_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $horizontal_url = $image_location.'/"
                                     +stat+"_horizontal_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $vertical_url = $image_location.'/"
                                     +stat+"_vertical_VVV_LLL_SSS_DDD.png';\n")
            stat_globvars_file.write("      $Exp1_name = '"+exp1+"';\n")
            stat_globvars_file.write("      $Exp2_name = '"+exp2+"';\n")
            stat_globvars_file.write("      $Exp1_00_name = '"+exp1+"_00Z';\n")
            stat_globvars_file.write("      $Exp2_00_name = '"+exp2+"_00Z';\n")
            stat_globvars_file.write("      $Exp1_12_name = '"+exp1+"_12Z';\n")
            stat_globvars_file.write("      $Exp2_12_name = '"+exp2+"_12Z';\n")
            stat_globvars_file.write("      $Global_name = 'gl';\n")
            stat_globvars_file.write("      $NHem_name = 'nh';\n")
            stat_globvars_file.write("      $SHem_name = 'sh';\n")
            stat_globvars_file.write("      $Tropics_name = 'tr';\n")
            stat_globvars_file.write("      $NAmer_name = 'na';\n")
            stat_globvars_file.write("      $CONUS_name = 'us';\n")
            stat_globvars_file.write("      $Eur_name = 'eu';\n")
            stat_globvars_file.write("      $Asia_name = 'as';\n")
            stat_globvars_file.write("      $AllReg_name = 'all';\n")
            stat_globvars_file.write("      $Temp_name = 't';\n")
            stat_globvars_file.write("      $Pres_name = 'p';\n")
            stat_globvars_file.write("      $GeoHgt_name = 'z';\n")
            stat_globvars_file.write("      $SpefHum_name = 'q';\n")
            stat_globvars_file.write("      $VectWind_name = 'w';\n")
            stat_globvars_file.write("      $Tropo_name = 't';\n")
            stat_globvars_file.write("      $Strato_name = 's';\n")
            stat_globvars_file.write("      $P20_name = '20';\n")
            stat_globvars_file.write("      $P30_name = '30';\n")
            stat_globvars_file.write("      $P50_name = '50';\n")
            stat_globvars_file.write("      $P70_name = '70';\n")
            stat_globvars_file.write("      $P100_name = '100';\n")
            stat_globvars_file.write("      $P150_name = '150';\n")
            stat_globvars_file.write("      $P200_name = '200';\n")
            stat_globvars_file.write("      $P250_name = '250';\n")
            stat_globvars_file.write("      $P300_name = '300';\n")
            stat_globvars_file.write("      $P400_name = '400';\n")
            stat_globvars_file.write("      $P500_name = '500';\n")
            stat_globvars_file.write("      $P700_name = '700';\n")
            stat_globvars_file.write("      $P850_name = '850';\n")
            stat_globvars_file.write("      $P925_name = '925';\n")
            stat_globvars_file.write("      $P1000_name = '1000';\n")
            stat_globvars_file.write("      $Sfc_name = 'sfc';\n")
            stat_globvars_file.write("      $AnlGes_00_name = 'anl_ges_00Z';"
                                     +"\n")
            stat_globvars_file.write("      $AnlGes_12_name = 'anl_ges_12Z';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr12_Fhr36_name = 'f12_f36';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr24_Fhr48_name = 'f24_f48';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr00Fhr06_name = 'f00af06';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr12Fhr36_name = 'f12af36';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr24Fhr48_name = 'f24af48';"
                                     +"\n")
            stat_globvars_file.write("      $Fhr00_name = 'f00';\n")
            stat_globvars_file.write("      $Fhr06_name = 'f06';\n")
            stat_globvars_file.write("      $Fhr12_name = 'f12';\n")
            stat_globvars_file.write("      $Fhr24_name = 'f24';\n")
            stat_globvars_file.write("      $Fhr36_name = 'f36';\n")
            stat_globvars_file.write("      $Fhr48_name = 'f48';\n")
            stat_globvars_file.write("      $Fhr60_name = 'f60';\n")
            stat_globvars_file.write("      $Fhr72_name = 'f72';\n")
            stat_globvars_file.write("      $Fhr84_name = 'f84';\n")
            stat_globvars_file.write("      $Fhr96_name = 'f96';\n")
            stat_globvars_file.write("      $Fhr108_name = 'f108';\n")
            stat_globvars_file.write("      $Fhr120_name = 'f120';\n")
            stat_globvars_file.write("      $LeadAll_name = 'all';\n")
            stat_globvars_file.write("      $LeadAllExp1_name = 'all-"
                                     +exp1+"';\n")
            stat_globvars_file.write("      $LeadAllExp2_name = 'all-"
                                     +exp2+"';\n")
            stat_globvars_file.write("      $LeadMean_name = 'timeout';?>\n")
            stat_globvars_file.write('<script type="text/javascript">var '
                                     +'exp1 = "<?= $Exp1_name ?>";</script>\n')
            stat_globvars_file.write('<script type="text/javascript">var '
                                     +'exp2 = "<?= $Exp2_name ?>";</script>\n')
            stat_globvars_file.write('<script type="text/javascript" '
                                     +'src="../function_vsdb.js"></script>\n')
    # Rename fit2obs images
    src_images_dir = os.path.join(DATA, RUN, 'fit2obs', 'web', 'fits')
    dest_images_dir = os.path.join(fit2obs_plots_dir, 'images')
    if not os.path.exists(dest_images_dir):
        os.makedirs(dest_images_dir)
    plot_type_list = [exp1, exp2, 'f00af06', 'f12af36', 'f24af48', 'timeout']
    region_list = ['gl', 'nh', 'sh', 'tr', 'na', 'us', 'eu', 'as', 'all']
    ob_type_dict = {
        'ADPUPA': 'adp',
        'ADPSFC': 'sfc',
        'SFCSHP': 'shp',
        'AIRCFT': 'acft',
        'AIRCAR': 'acar'
    }
    for plot_type in plot_type_list:
        src_plot_type_dir = os.path.join(src_images_dir, 'time', plot_type)
        for ob_type in list(ob_type_dict.keys()):
            if ob_type == 'ADPUPA':
                var_list = ['t', 'z', 'q', 'w']
                level_list = ['1000', '925', '850', '700', '500', '400',
                              '300', '250', '200', '150', '100',
                              '70', '50', '30', '20']
            elif ob_type in ['ADPSFC', 'SFCSHP']:
                var_list = ['t', 'p', 'q', 'w']
                level_list = ['sfc']
            elif ob_type in ['AIRCAR', 'AIRCFT']:
                var_list = ['t', 'w']
                level_list = ['1000', '700', '300']
            for var in var_list:
                for level in level_list:
                    if level == 'sfc':
                        level_original = ''
                    else:
                        level_original = level
                    for region in region_list:
                        rmse_src = os.path.join(
                            src_plot_type_dir,
                            var+level_original+'.'+region+'.'
                            +ob_type_dict[ob_type]+'.png'
                        )
                        rmse_dest = os.path.join(
                             dest_images_dir,
                            'rmse_'+ob_type+'_'+var+'_'+level+'_'
                            +plot_type+'_'+region+'.png'
                        )
                        bias_src = os.path.join(
                            src_plot_type_dir,
                            var+'b'+level_original+'.'+region+'.'
                            +ob_type_dict[ob_type]+'.png'
                        )
                        bias_dest = os.path.join(
                             dest_images_dir,
                            'bias_'+ob_type+'_'+var+'_'+level+'_'
                            +plot_type+'_'+region+'.png'
                        )
                        if os.path.exists(rmse_src):
                            shutil.copy(rmse_src, rmse_dest)
                        if os.path.exists(bias_src):
                            shutil.copy(bias_src, bias_dest)
    src_horizontal_dir = os.path.join(src_images_dir, 'horiz')
    plot_type_list = ['f00', 'f06', 'f12', 'f24', 'f36', 'f48',
                      'all-'+exp1, 'all-'+exp2]
    region_list = ['us', 'eu', 'as']
    var_list = ['t', 'z', 'q', 'w']
    level_list = ['925', '850', '700', '500', '200']
    for var in var_list:
        for level in level_list:
            for region in region_list:
                for plot_type in plot_type_list:
                    if plot_type == 'all-'+exp1:
                        src_horizontal_plot_type_dir  = os.path.join(
                            src_horizontal_dir, exp1
                        )
                    else:
                        src_horizontal_plot_type_dir  = os.path.join(
                            src_horizontal_dir, exp2
                        )
                    if 'all' in plot_type:
                        rmse_src = os.path.join(
                            src_horizontal_plot_type_dir,
                            var+level+'.all.'+region+'.rmse.png'
                        )
                        bias_src = os.path.join(
                            src_horizontal_plot_type_dir,
                            var+level+'.all.'+region+'.bias.png'
                        )
                    else:
                        rmse_src = os.path.join(
                            src_horizontal_plot_type_dir,
                            var+level+'.'+plot_type+'.'+region+'.rmse.png'
                        )
                        bias_src = os.path.join(
                            src_horizontal_plot_type_dir,
                            var+level+'.'+plot_type+'.'+region+'.bias.png'
                        )
                    rmse_dest = os.path.join(
                        dest_images_dir,
                        'rmse_horizontal_'+var+'_'+level+'_'
                        +plot_type+'_'+region+'.png'
                    )
                    bias_dest = os.path.join(
                        dest_images_dir,
                        'bias_horizontal_'+var+'_'+level+'_'
                        +plot_type+'_'+region+'.png'
                    )
                    if os.path.exists(rmse_src):
                        shutil.copy(rmse_src, rmse_dest)
                    if os.path.exists(bias_src):
                        shutil.copy(bias_src, bias_dest)
    src_timevrt_dir = os.path.join(src_images_dir, 'time', 'timevrt')
    src_vert_dir = os.path.join(src_images_dir, 'vert')
    plot_type_list = ['f00', 'f12', 'f24', 'f36', 'f48', 'f60', 'f72',
                      'f84', 'f96', 'f108', 'f120', exp1+'_00Z', exp2+'_00Z',
                      exp1+'_12Z', exp2+'_12Z','anl_ges_00Z', 'anl_ges_12Z',
                      'f12_f36', 'f24_f48']
    region_list = ['gl', 'nh', 'sh', 'tr', 'na', 'us', 'eu', 'as', 'all']
    level_list = ['t', 's']
    var_list = ['t', 'z', 'q', 'w']
    for var in var_list:
        for level in level_list:
            for region in region_list:
                for plot_type in plot_type_list:
                    if plot_type[0] == 'f' and len(plot_type.split('_')) == 1:
                        rmse_src = os.path.join(
                            src_timevrt_dir,
                            level+var+'.'+region+'.'+plot_type[1:]+'.png'
                        )
                        bias_src = os.path.join(
                            src_timevrt_dir,
                            level+var+'b.'+region+'.'+plot_type[1:]+'.png'
                        )
                    elif plot_type \
                            in [exp1+'_00Z', exp2+'_00Z', exp1+'_12Z',
                                exp2+'_12Z']:
                        exp = plot_type.split('_')[0]
                        hr = plot_type.split('_')[1]
                        if hr == '00Z':
                            hr_original = '0z'
                        else:
                            hr_original = hr.lower()
                        rmse_src = os.path.join(
                            src_vert_dir, exp,
                            level+var+'.'+hr_original+'.'+region+'.adp.png'
                        )
                        bias_src = os.path.join(
                            src_vert_dir, exp,
                            level+var+'.'+hr_original+'.'+region+'.adp.png'
                        )
                    elif plot_type \
                            in ['anl_ges_00Z', 'anl_ges_12Z', 'f12_f36',
                                'f24_f48']:
                        if 'anl' in plot_type:
                            rmse_src = os.path.join(
                                src_vert_dir, exp1+'-'+exp2,
                                level+var+'.f00.'
                                +plot_type.split('_')[2].lower()
                                +'.'+region+'.adp.png'
                            )
                            bias_src = os.path.join(
                                src_vert_dir, exp1+'-'+exp2,
                                level+var+'.f00.'
                                +plot_type.split('_')[2].lower()
                                +'.'+region+'.adp.png'
                            )
                        else:
                            rmse_src = os.path.join(
                                src_vert_dir, exp1+'-'+exp2,
                                level+var+'.'+plot_type.split('_')[0]
                                +'.'+region+'.adp.png'
                            )
                            bias_src = os.path.join(
                                src_vert_dir, exp1+'-'+exp2,
                                level+var+'.'+plot_type.split('_')[0]
                                +'.'+region+'.adp.png'
                            )
                    rmse_dest = os.path.join(
                        dest_images_dir,
                        'rmse_vertical_'+var+'_'+level+'_'
                        +plot_type+'_'+region+'.png'
                    )
                    bias_dest = os.path.join(
                        dest_images_dir,
                        'bias_vertical_'+var+'_'+level+'_'
                        +plot_type+'_'+region+'.png'
                    )
                    if os.path.exists(rmse_src):
                        shutil.copy(rmse_src, rmse_dest)
                    if os.path.exists(bias_src):
                        shutil.copy(bias_src, bias_dest)

# Create job card
web_job_filename = os.path.join(DATA, 'batch_jobs',
                                NET+'_'+RUN+'_web.sh')
with open(web_job_filename, 'a') as web_job_file:
        web_job_file.write('#!/bin/sh'+'\n')
        web_job_file.write('set -x'+'\n')
        if machine == 'WCOSS2':
            web_job_file.write('cd $PBS_O_WORKDIR\n')
        web_job_file.write('ssh -q -l '+webhostid+' '+webhost+' " ls -l '
                           +webdir+' "'+'\n')
        web_job_file.write('if [ $? -ne 0 ]; then'+'\n')
        web_job_file.write('    echo "Making directory '+webdir+'"'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                           +' "mkdir -p '+webdir+' "'+'\n')
        web_job_file.write('    sleep 30\n')
        web_job_file.write('    scp -q '+os.path.join(USHverif_global,
                                                      'webpage.tar')+'  '
                           +webhostid+'@'+webhost+':'+webdir+'/.'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                           +' "cd '+webdir+' ; tar -xvf webpage.tar "'+'\n')
        web_job_file.write('    ssh -q -l '+webhostid+' '+webhost
                           +' "rm '+os.path.join(webdir, 'webpage.tar')
                           +' "'+'\n')
        web_job_file.write('fi'+'\n')
        web_job_file.write('\n')
        if RUN == 'fit2obs_plots':
            web_job_file.write('scp -r '+ os.path.join(DATA, RUN, 'images')
                               +' '+webhostid+'@'+webhost+':'
                               +os.path.join(webdir, RUN_type, '.')+'\n')
        else:
            web_job_file.write('scp -r '+os.path.join(DATA, RUN,
                                                      'metplus_output',
                                                      'images')
                               +' '+webhostid+'@'+webhost+':'
                               +os.path.join(webdir, RUN_type, '.')+'\n')
        if RUN == 'tropcyc':
            for tropcyc_type in ['intensityerr', 'trackerr']:
                web_job_file.write(
                    'scp -r '+os.path.join(DATA, RUN,
                                           'create_webpage_templates',
                                           tropcyc_type, tropcyc_type+'*.php')
                    +' '+webhostid+'@'+webhost+':'
                    +os.path.join(webdir, RUN_type, tropcyc_type, '.\n')
                )
        elif RUN == 'fit2obs_plots':
            for stat in ['bias', 'rmse']:
                web_job_file.write('scp -r '+os.path.join(DATA, RUN,
                                                          stat
                                                          +'_globalvars.php')
                                   +' '+webhostid+'@'+webhost+':'
                                   +os.path.join(webdir, RUN_type, stat, '.\n')
                )
        if KEEPDATA == 'NO':
            web_job_file.write('\n')
            web_job_file.write('cd ..\n')
            web_job_file.write('rm -rf '+RUN)

# Submit job card
os.chmod(web_job_filename, 0o755)
web_job_output = web_job_filename.replace('.sh', '.out')
web_job_name = web_job_filename.rpartition('/')[2].replace('.sh', '')
print("Submitting "+web_job_filename+" to "+QUEUESERV)
print("Output sent to "+web_job_output)
if machine == 'WCOSS2':
    os.system('qsub -V -l walltime='+walltime.strftime('%H:%M:%S')+' '
              +'-q '+QUEUESERV+' -A '+ACCOUNT+' -o '+web_job_output+' '
              +'-e '+web_job_output+' -N '+web_job_name+' '
              +'-l select=1:ncpus=1 '+web_job_filename)
elif machine == 'HERA':
    os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
                  +'--partition='+QUEUESERV+' --account='+ACCOUNT+' '
                  +'--output='+web_job_output+' '
                  +'--job-name='+web_job_name+' '+web_job_filename)
elif machine == 'JET':
    if webhost == 'emcrzdm.ncep.noaa.gov':
        print("ERROR: Currently "+machine.title()+" cannot connect to "
              +webhost)
    else:
        os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
                  +'--partition='+QUEUESERV+' --account='+ACCOUNT+' '
                  +'--output='+web_job_output+' '
                  +'--job-name='+web_job_name+' '+web_job_filename)
elif machine == 'ORION':
    if webhost == 'emcrzdm.ncep.noaa.gov':
        print("ERROR: Currently Orion cannot connect to "+webhost)
    else:
        os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
                  +'--partition='+QUEUESERV+' --account='+ACCOUNT+' '
                  +'--output='+web_job_output+' '
                  +'--job-name='+web_job_name+' '+web_job_filename)
elif machine == 'S4':
    if webhost == 'emcrzdm.ncep.noaa.gov':
        print("ERROR: Currently S4 cannot connect to "+webhost)
    else:
        os.system('sbatch --ntasks=1 --time='+walltime.strftime('%H:%M:%S')+' '
                  +'--partition='+QUEUESERV+' --account='+ACCOUNT+' '
                  +'--output='+web_job_output+' '
                  +'--job-name='+web_job_name+' '+web_job_filename)

print("END: "+os.path.basename(__file__))
