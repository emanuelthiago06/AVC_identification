import pandas as pd
import numpy as np
import cv2
from imutils import paths
import mahotas as mt
import os
import pydicom as dy
import re

def get_jan(**kwargs):
    image = kwargs["img"]
    janela = kwargs["jan"]
    
    arraynp = image.copy().astype(np.float128)
    offset = min(janela)
    
    arraynp = arraynp - offset
    arraynp = np.where(arraynp >=max(janela),(max(janela)-offset),arraynp)
    arraynp = np.where(arraynp <min(janela),0,arraynp)
    arraynp = (arraynp/(max(janela)-offset))*255
    
    return arraynp.astype(np.uint8)

def run_haralick(impath):
	regex_pattern = r"^Paciente(?P<numero_paciente>\d*)\s*\((?P<slice>\d*)\).dcm"
	count = 0
	data = []
	j = 0
	contador = 0
	list_test = []
	list_number = []
	all_directory_paths = os.scandir(impath)
	for directory in all_directory_paths:
		for imagePath in os.scandir(directory.path):
			match = re.match(regex_pattern,imagePath.name)
			numero_paciente = match.group("numero_paciente")
			slice_paciente = match.group("slice")
			patient = dy.dcmread(imagePath.path)
			patient_sex = patient.PatientSex
			patient_age = patient.PatientAge
			janelamento = np.arange(10,120)
			img_jan = get_jan(img = patient.pixel_array,jan = janelamento)
			#gray = cv2.cvtColor(img_jan, cv2.COLOR_BGR2GRAY) #change the color of the image to gray
			histt = mt.features.haralick(img_jan,return_mean_ptp = True)
			hist = np.ravel(histt)
			count = 1+count
			if count == 1:
				va = hist.transpose()
			if count == 2:
				vb = hist.transpose()
			if count == 3:
				vc = hist.transpose()
				histd = np.hstack((va, vb, vc)) #hstack put the var,varb,varc in the same line
				dataframepandas = np.hstack((numero_paciente,slice_paciente,patient_sex,patient_age, va, vb, vc))#hstack put the rotulostemp, zclass var,varb,varc in the same line
				list_number.append(numero_paciente)
				data.append(dataframepandas) #put the dataframepandas variable into dados  #mudar para o numpy array
				count = 0
				j = j + 1
			tam = va.size
		contador+=1
		print(f"{contador*50} Pacientes concluidos de 300")
		
	return data,list_number,tam


def put_class(my_list,path_plan):
	regex_pattern = r"Paciente(?P<numero>\d*)"
	db_plan = pd.read_csv(path_plan)
	count = 0
	count2 = 0
	class_list = []
	list_class = db_plan.iloc[:,9].to_list()
	list_name = db_plan.iloc[:,1].to_list()
	for i in my_list:
		for j in list_name:
			matche = re.match(regex_pattern,j)
			try:
				numero = matche.group("numero")
			except:
				continue
			if i == numero:
				class_list.append(list_class[count2])
				count+=1
				break
			count2+=1
		count2 = 0
		if count == 0:
			class_list.append('10')
		count = 0
	return class_list


def create_csv(dataframe,ncolumns,class_list):
	df = pd.DataFrame(dataframe,columns=ncolumns) #create the pandas dataframe
	df["classe"] = class_list
	df.to_csv('results_haralick_tomo.csv') #create the csv file from pandas dataframe

def define_columns(tam):
	nomes_col = ["numero_paciente","slice_paciente","patient_sex","patient_age"] #create the column segment for the pandas dataframe
	count3 = 0
	while count3 < (tam): #count the vara and create the columns
		name = "x_"+str(count3)
		count3 = count3+1
		nomes_col.append(name)
	count3 = 0
	while count3 < (tam): #count the varb and create the columns
		name = "y_"+str(count3)
		count3 = count3+1
		nomes_col.append(name)
	count3 = 0
	while count3 < (tam): #count the varc and create the columns
		name = "z_"+str(count3)
		count3 = count3+1
		nomes_col.append(name)
	return nomes_col


def main():
	path = "/home/gpds/Documentos/imagens-médicas/projeto_cecilia/avc-pacientes-renomeados"
	path_plan = "/home/gpds/Documentos/imagens-médicas/projeto_cecilia/Planilha_de_controle AVC 15_12_14.csv"
	data,list_number,tam = run_haralick(path)
	class_list = put_class(list_number,path_plan)
	nomes_col = define_columns(tam)
	create_csv(data,nomes_col,class_list)

main()
