# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 17:20:14 2020

@author: splathottam
"""

import os

md_files_for_word = ['user_guide_title.md','user_guide_TOC.md',
                     'user_guide_introduction.md','user_guide_getting_started.md',
                     'user_guide_configuration_template.md','user_guide_visualization_analytics.md',
                     'user_guide_understanding_config.md',
                     'user_guide_cosimulation_details.tex.md','user_guide_capability_and_limitations.md',
                     'user_guide_advanced_usage.md','user_guide_software_details.md',
                     'user_guide_performance.md',
                     'examples/Example_1_DER_trip_and_ridethrough.md',
                     'examples/Example_2_DER_penetration_and_steadystate.md',
                     'user_guide_installation.md','user_guide_sys_requirements.md',
                     'user_guide_references.md','user_guide_DER_parameters.md']

md_files_for_pdf = ['user_guide_title.md','user_guide_TOC.md',
                     'user_guide_introduction.md','user_guide_getting_started.md',
                     'user_guide_configuration_template.md','user_guide_visualization_analytics.md',
                     'user_guide_understanding_config.md',
                     'user_guide_cosimulation_details.md','user_guide_capability_and_limitations.md',
                     'user_guide_advanced_usage.md','user_guide_software_details.md',
                     'user_guide_performance.md',
                     'examples/Example_1_DER_trip_and_ridethrough.md',
                     'examples/Example_2_DER_penetration_and_steadystate.md',
                     'user_guide_installation.md','user_guide_sys_requirements.md',
                     'user_guide_references.md','user_guide_DER_parameters.md']
"""
md_files_for_pdf =['user_guide_title.md','user_guide_TOC.md','user_guide_introduction.md',
                     'user_guide_getting_started.md',
                     'user_guide_cosimulation_details.md','user_guide_capability_and_limitations.md',
                     'user_guide_advanced_usage.md','user_guide_software_details.md',
                     'examples/Example_1_test_of_DER_RT_and_trip.md.md',
                     'examples/Example_2_system_state_initialization_test.md',
                     'examples/Example_3_test_of_DER_RT_and_trip.md',
                     'examples/Example_4_test_of_DER_RT_and_trip.md',
                     'user_guide_installation.md','user_guide_sys_requirements.md',
                     'user_guide_references.md']
"""
md_files_for_word_string = ''
md_files_for_pdf_string = ''

output_word_filename = 'TDcoSim_user_guide_version_2_0.docx'
output_pdf_filename = 'TDcoSim_user_guide_version_2_0.pdf'


for md_file in md_files_for_word:    
    md_files_for_word_string = md_files_for_word_string + ' '  + md_file
for md_file in md_files_for_pdf:    
    md_files_for_pdf_string = md_files_for_pdf_string + ' '  + md_file    

#os.system('pandoc user_guide_title.md -o test.pdf')
md2word_commandstring = 'pandoc '+ md_files_for_word_string +  ' -o ' + output_word_filename + ' --resource-path=.;./examples/use_case_results/'
md2pdf_commandstring = 'pandoc '+ md_files_for_pdf_string +  ' -o ' + output_pdf_filename + ' --resource-path=.;examples/use_case_results'

print(f'Creating word document from Markdown files:{output_word_filename}')
print(f'Command string:{md2word_commandstring}')
os.system(md2word_commandstring)

print(f'Creating pdf document from Markdown files:{output_pdf_filename}')
print(f'Command string:{md2pdf_commandstring}')
os.system(md2pdf_commandstring)
