from pyxnat import Interface


xnat = Interface(server='https://xnat.nyspi.org', user='grayjoh', password='jack123')
#, user='grayjoh', password='jack123'
# xnat.save_config('xnat.cfg')
# xnat2 = Interface(config='xnat.cfg')
#print list(xnat.select.projects())

# print xnat.select('//exams').get()
#\
print list(xnat.select('/projects/test/subjects//experiments//scans/*'))

#print xnat.inspect.structure()

projectName = 'test'
constraints = [('xnat:subjectData/PROJECT', '=', projectName)]

#print xnat.select('//files').where(constraints)





















# from selenium import webdriver
# from selenium.webdriver import Chrome
# from selenium.webdriver.common.keys import Keys


# webdriver = '/chromedriver'
# driver = Chrome(webdriver)



# # WIP: input xnat description instead of url
# #xnat_desc = raw_input("Enter XNAT description of project to scan: ")
# xnat_desc = 'steipedi'
# project_root_url = 'https://xnat.nyspi.org/data/projects/'+ xnat_desc + '?format=html'
# subject_url = 'https://xnat.nyspi.org/app/action/DisplayItemAction/search_value/XNATnyspi_S03695/search_element/xnat:subjectData/search_field/xnat:subjectData.ID/project/steipedi'
# session_url = 'https://xnat.nyspi.org/app/action/DisplayItemAction/search_element/xnat%3AmrSessionData/search_field/xnat%3AmrSessionData.ID/search_value/XNATnyspi_E04822/popup/false/project/steipedi'
# # open xnat session to access page with auth
# with requests.Session() as session:
#     post = session.post(login_url, data=payload)
#     res = session.get(project_root_url)

#     driver.get(project_root_url)
#     assert "Python" in driver.title