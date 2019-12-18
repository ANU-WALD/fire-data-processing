import os

version = '1'

proj_name = 'fire_deciles'
proj_path = '/g/data/xc0/user/ali/code'

proj_org_path = proj_path + '/' + proj_name
proj_zip_path_file = proj_path + '/' + 'VOID_' + proj_name + '_v' + version + '.zip'

zip_cmd = 'zip -r -j ' + proj_zip_path_file + ' ' + proj_org_path

print(zip_cmd)

os.system(zip_cmd)
