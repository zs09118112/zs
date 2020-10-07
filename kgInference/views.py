from django.http import HttpResponse
from django.shortcuts import render
from ormDesign.models import *
import Levenshtein
from django.db.models import Max,Min,Count,Sum,Avg
import math
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from io import BytesIO
import base64
from matplotlib.pyplot import MultipleLocator


# Create your views here.
def helloworld(request):
    return HttpResponse('Hello World! by kgInference group')

#Get certain major scores in different univ. and rank them  信息统计组数据需求

def getMajorScoresRanking(pID,cID,y,mName):
    #参数为省份ID（整数1-34），科类ID（整数1-3），年份（整数）和专业名称
    majorList=Majors.objects.filter(provinceID=pID,
                                    categoryID=cID,
                                    year=y,
                                    majorName=mName)
    scoresDict={}
    for major in majorList:
        scoresDict[major.collegeID.collegeName]=major.minScore
    #return scoresDict
    scoresOrder=dict(sorted(scoresDict.items(), key = lambda kv:kv[1],reverse=True))
    return scoresOrder

#Get the number of 985,211 and top in every province   地图组数据需求
def get_data_985():
    list_985=[]
    for i_ in range(1,35):
        count_985=Colleges.objects.filter(provinceID=i_,project985=True).aggregate(Count('collegeID'))
        list_985.append(count_985['collegeID__count'])
    return list_985


def get_data_211():
    list_211=[]
    for i_ in range(1,35):
        count_211=Colleges.objects.filter(provinceID=i_,project211=True).aggregate(Count('collegeID'))
        list_211.append(count_211['collegeID__count'])
    return list_211


def get_data_top():
    list_top=[]
    for i_ in range(1,35):
        count_top=Colleges.objects.filter(provinceID=i_,top=True).aggregate(Count('collegeID'))
        list_top.append(count_top['collegeID__count'])
    return list_top

def get_data():
    series=[]
    list_985=get_data_985()
    list_211=get_data_211()
    list_top=get_data_top()
    for i_ in range(0,34):
        temp={}
        province=Provinces.objects.filter(provinceID=i_+1)
        temp["name"]=province[0].provinceName
        temp["value"]=i_
        temp["project985"]=list_985[i_]
        temp["project211"]=list_211[i_]
        temp["doubleTop"]=list_top[i_]
        series.append(temp)
    return series

def KgBaseInfoFillin(request):
    majorlist=Majors.objects.values_list('majorName',flat=True).distinct()
    provincelist=Provinces.objects.values_list('provinceName',flat=True).distinct()
    return render(request,'KgBaseInfoFillin.html',{'majorlist':majorlist,'provincelist':provincelist})
    
def InfoIntoQuestions(request):         #将用户输入信息转化成更具体的问题供用户选择
    province = request.POST.get('province')
    score = request.POST.get('score')
    score = int(score)
    category = request.POST.get('category')
    targetprovince = request.POST.get('Tprovince')
    targetmajor = request.POST.get('Tmajor')
    questions = []

    if(targetprovince == "" and targetmajor == ""):
        questionhead = province + category + str(score) + "分"
        question11 = questionhead + "冲一冲能上什么学校？"
        question12 = questionhead + "稳一稳能上什么学校？"
        question13 = questionhead + "保一保能上什么学校？"
        questions.append(question11)
        questions.append(question12)
        questions.append(question13)

        if(province == "江苏"):
            if(score >= 390):
                question14 = questionhead + "能上什么985学校?"
                questions.append(question13)
            if (score >= 370 and score < 390):
                question14 = questionhead + "能上什么985学校?"
                question15 = questionhead + "能上什么211学校?"
                questions.append(question14)
                questions.append(question15)
            if (score < 370 and score >= 360):
                question14 = questionhead + "能上什么211学校?"
                question15 = questionhead + "能上什么一本学校？"
                questions.append(question14)
                questions.append(question15)
            if(score < 360):
                question14 = questionhead + "能上什么一本学校？"
                questions.append(question14)

        elif(province == "上海"):
            if(score >= 560):
                question14 = questionhead + "能上什么985学校?"
                questions.append(question14)
            if (score >= 510 and score < 560):
                question14 = questionhead + "能上什么985学校?"
                question15 = questionhead + "能上什么211学校?"
                questions.append(question14)
                questions.append(question15)
            if (score < 510 and score >= 450):
                question14 = questionhead + "能上什么211学校?"
                question15 = questionhead + "能上什么一本学校？"
                questions.append(question14)
                questions.append(question15)
            if(score < 450):
                question14 = questionhead + "能上什么一本学校？"
                questions.append(question14)

        else:
            if(score >= 660):
                question14 = questionhead + "能上什么985学校?"
                questions.append(question14)
            if (score >= 620 and score < 660):
                question14 = questionhead + "能上什么985学校?"
                question15 = questionhead + "能上什么211学校?"
                questions.append(question14)
                questions.append(question15)
            if (score < 620 and score >= 590):
                question14 = questionhead + "能上什么211学校?"
                question15 = questionhead + "能上什么一本学校?"
                questions.append(question14)
                questions.append(question15)
            if(score < 590):
                question14 = questionhead + "能上什么一本学校？"
                questions.append(question14)


    if(targetprovince != "" and targetmajor == ""):
        questionhead = province + category + str(score) + "分"
        question21 = questionhead + "冲一冲能上" + targetprovince + "的什么学校？"
        question22 = questionhead + "稳一稳能上" + targetprovince + "的什么学校？"
        question23 = questionhead + "稳一稳能上" + targetprovince + "的什么学校？"
        question24 = targetprovince + "大学在本省" + category + "的录取分数线排名"

        questions.append(question21)
        questions.append(question22)
        questions.append(question23)
        questions.append(question24)

        if(province == "江苏"):
            if(score >= 390):
                question25 = questionhead + "能上" + targetprovince + "的什么985学校?"
                questions.append(question25)
            if (score >= 370 and score < 390):
                question25 = questionhead + "能上" + targetprovince + "的什么985学校?"
                question26 = questionhead + "能上" + targetprovince + "的什么211学校?"
                questions.append(question25)
                questions.append(question26)
            if (score < 370 and score >= 360):
                question25 = questionhead + "能上" + targetprovince + "的什么211学校?"
                question26 = questionhead + "能上" + targetprovince + "的什么一本学校？"
                questions.append(question25)
                questions.append(question26)
            if(score < 360):
                question25 = questionhead + "能上" + targetprovince + "的什么一本学校？"
                questions.append(question25)

        elif(province == "上海"):
            if(score >= 560):
                question25 = questionhead + "能上" + targetprovince + "的什么985学校?"
                questions.append(question25)
            if (score >= 510 and score < 560):
                question25 = questionhead + "能上" + targetprovince + "的什么985学校?"
                question26 = questionhead + "能上" + targetprovince + "的什么211学校?"
                questions.append(question25)
                questions.append(question26)
            if (score < 510 and score >= 450):
                question25 = questionhead + "能上" + targetprovince + "的什么211学校?"
                question26 = questionhead + "能上" + targetprovince + "的什么一本学校？"
                questions.append(question25)
                questions.append(question26)
            if(score < 450):
                question25 = questionhead + "能上" + targetprovince + "的什么一本学校？"
                questions.append(question25)

        else:
            if(score >= 660):
                question25 = questionhead + "能上" + targetprovince + "什么985学校?"
                questions.append(question25)
            if (score >= 620 and score < 660):
                question25 = questionhead + "能上" + targetprovince + "的什么985学校?"
                question26 = questionhead + "能上" + targetprovince + "的什么211学校?"
                questions.append(question25)
                questions.append(question26)
            if (score < 620 and score >= 590):
                question25 = questionhead + "能上" + targetprovince + "的什么211学校?"
                question26 = questionhead + "能上" + targetprovince + "的什么一本学校?"
                questions.append(question25)
                questions.append(question26)
            if(score < 590):
                question25 = questionhead + "能上" + targetprovince + "的什么一本学校？"
                questions.append(question25)

    if(targetprovince == "" and targetmajor != ""):
        question31 = targetmajor + "专业" + "全国大学在本省的录取分数线排名？"
        question32 = province + category + str(score) + "分" + "能上哪些学校的" + targetmajor + "专业？"
        questions.append(question31)
        questions.append(question32)

        questionhead = province + category + str(score) + "分"
        question33 = questionhead + "冲一冲能上" + "什么学校？"
        question34 = questionhead + "稳一稳能上" + "什么学校？"
        question35 = questionhead + "稳一稳能上" + "什么学校？"

        questions.append(question33)
        questions.append(question34)
        questions.append(question35)

    if(targetprovince != "" and targetmajor != ""):
        question41 = targetmajor + "专业" + targetmajor + "省的大学在" + targetprovince + "省的录取分数排名"
        #questions.append(question41)
        questions.append(question41)

        questionhead = province + category + str(score) + "分"
        question42 = questionhead + "冲一冲能上" + targetprovince + "的什么学校？"
        question43 = questionhead + "稳一稳能上" + targetprovince + "的什么学校？"
        question44 = questionhead + "稳一稳能上" + targetprovince + "的什么学校？"
        question45 = targetprovince + "大学在本省" + category + "的录取分数线排名"

        questions.append(question42)
        questions.append(question43)
        questions.append(question44)
        questions.append(question45)

        questionhead = province + category + str(score) + "分能上什么" + targetprovince + "省的大学？"
        if(province == "江苏"):
            if(score >= 390):
                question46 = questionhead + "985学校?"
                questions.append(question46)
            if (score >= 370 and score < 390):
                question46 = questionhead + "985学校?"
                question47 = questionhead + "211学校?"
                questions.append(question46)
                questions.append(question47)
            if (score < 370 and score >= 360):
                question46 = questionhead + "211学校?"
                question47 = questionhead + "一本学校？"
                questions.append(question46)
                questions.append(question47)
            if(score < 360):
                question46 = questionhead + "能上" + targetprovince + "的什么一本学校？"
                questions.append(question46)

        elif(province == "上海"):
            if(score >= 560):
                question46 = questionhead + "985学校?"
                questions.append(question46)
            if (score >= 510 and score < 560):
                question46 = questionhead + "985学校?"
                question47 = questionhead + "211学校?"
                questions.append(question46)
                questions.append(question47)
            if (score < 510 and score >= 450):
                question46 = questionhead + "211学校?"
                question47 = questionhead + "一本学校？"
                questions.append(question46)
                questions.append(question47)
            if(score < 450):
                question46 = questionhead + "能上" + targetprovince + "的什么一本学校？"
                questions.append(question46)

        else:
            if(score >= 660):
                question46 = questionhead + "985学校?"
                questions.append(question46)
            if (score >= 620 and score < 660):
                question46 = questionhead + "985学校?"
                question47 = questionhead + "211学校?"
                questions.append(question46)
                questions.append(question47)
            if (score < 620 and score >= 590):
                question46 = questionhead + "211学校?"
                question47 = questionhead + "一本学校?"
                questions.append(question46)
                questions.append(question47)
            if(score < 590):
                question46 = questionhead + "一本学校？"
                questions.append(question46)
    return render(request,'KgInfoToQuestion.html',{'questions':questions,'score':score})


def getSimilarity(str1, str2):
   return Levenshtein.ratio(str1, str2)



def ChooseFunction(request):
    question = request.POST.get('question')
    question = str(question)
    #首先判断选填内容是否填了
    tprovince = request.POST.get('Tprovince')
    tmajor = request.POST.get('Tmajor')        #tprovince/tmajor从前端传回

    tprovince = "all"
    tmajor = "all"

    questionModelList = []
    similarity = []
    #1.两个选填的都没填
    if(tprovince == "all" and tmajor == "all"):
        question11 = "**省*科**分冲一冲能上什么学校？"
        question12 = "**省*科**分稳一稳能上什么学校？"
        question13 = "**省*科**分保一保能上什么学校？"
        question14 = "**省*科**分能上什么/985学校/211学校/本科学校？"
        questionModelList = [question11, question12, question13, question14]
        similarity = [getSimilarity(question, i) for i in questionModelList]
        quesindex=similarity.index(max(similarity))
        switch = {
            0: QuestionsIntoAnswer11,
            1: QuestionsIntoAnswer12,
            2: QuestionsIntoAnswer13,
            3: QuestionsIntoAnswer14
        }
        switch[quesindex](request)


    if(tprovince != "all" and tmajor == "all"):
        question11 = "**省*科**分冲一冲能上***省的什么学校？"
        question12 = "**省*科**分稳一稳能上***省的什么学校？"
        question13 = "**省*科**分保一保能上***省的什么学校？"
        question14 = "***省大学在**省*科的分数线排名？"
        question15 = "**省*科**分能上**省的什么985学校/211学校/本科学校？"
        questionModelList = [question11, question12, question13, question14, question15]
        similarity = [getSimilarity(question, i) for i in questionModelList]
        quesindex=similarity.index(max(similarity))
        switch = {
            0: QuestionsIntoAnswer21,
            1: QuestionsIntoAnswer22,
            2: QuestionsIntoAnswer23,
            3: QuestionsIntoAnswer24,
            4: QuestionsIntoAnswer25,
        }
        switch[quesindex](request)

    if(tprovince == "all" and tmajor != "all"):
        question11 = "**专业全国大学在**省的录取分数线排名？"
        question12 = "**省*科*分能上哪些学校的**专业？"
        question13 = "**省*科**分冲一冲能上什么学校？"
        question14 = "**省*科**分稳一稳能上什么学校？"
        question15 = "**省*科**分保一保能上什么学校？"
        question16 = "**省*科**分能上什么/985学校/211学校/本科学校?"

        questionModelList = [question11, question12, question13, question14,question15, question16]
        similarity = [getSimilarity(question, i) for i in questionModelList]
        quesindex = similarity.index(max(similarity))
        switch = {
            0: QuestionsIntoAnswer31,
            1: QuestionsIntoAnswer32,
            2: QuestionsIntoAnswer11,
            3: QuestionsIntoAnswer12,
            4: QuestionsIntoAnswer13,
            5: QuestionsIntoAnswer14,
        }
        switch[quesindex](request)

    if (tprovince != "all" and tmajor != "all"):
        question11 = "**专业***省的大学在本省录取分数线排名？"
        question12 = "**省*科*分冲一冲能上***省的什么学校？"
        question13 = "**省*科*分稳一稳能上***省的什么学校？"
        question14 = "**省*科*分保一保能上***省的什么学校？"
        question15 = "**省*科**分能上**省的什么985学校/211学校/本科学校？"
        question16 = "**专业***省的大学在本省的录取分数线排名？"
        question17 = "**专业全国大学在本省的录取分数线排名？"
        questionModelList = [question11, question12, question13, question14,question15, question16]
        similarity = [getSimilarity(question, i) for i in questionModelList]
        quesindex = similarity.index(max(similarity))
        switch = {
            0: QuestionsIntoAnswer41,
            1: QuestionsIntoAnswer21,
            2: QuestionsIntoAnswer22,
            3: QuestionsIntoAnswer23,
            4: QuestionsIntoAnswer25,
            5: QuestionsIntoAnswer42,
            6: QuestionsIntoAnswer31,
        }
        switch[quesindex](request)

    return render(request, 'KgInfoAnswers.html', {})

def GetCollegeMinScore(collegeid, provinceid, categoryid, year):               #获得学校在某个省文科/理科某一年的最低录取分数
    collegeMajorScoreList = Majors.objects.filter(collegeID_id = collegeid, provinceID_id=provinceid, categoryID_id = categoryid, year=year)
    scores = []
    for i in collegeMajorScoreList:
        scores.append(int(i.minScore))
    minscore = 0
    if len(scores):    #若列表不为空
        minscore = min(scores)
    return minscore

def GetCollegeAverageMinScore(collegeid, provinceid, categoryid):              #获得学校在某个省文科/理科三年的最低录取分数
    average = (GetCollegeMinScore(collegeid, provinceid, categoryid, 2019)+
              GetCollegeMinScore(collegeid, provinceid, categoryid, 2018)+
              GetCollegeMinScore(collegeid, provinceid, categoryid, 2017))/3
    return average

def VisualazationCollegeScore(collegelist, collegeMinScorelist, figureName):    #作图
    x = [i for i in range(len(collegelist))]
    width = 0.2
    index = np.arange(len(collegelist))

    for xx, yy in zip(x, collegeMinScorelist):
        plt.text(xx, yy + 2, str(yy), ha='center')
    figsize = (10, 8)

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.bar(index, collegeMinScorelist, width, color="#87CEFA")

    plt.ylabel('score', fontsize = 20)
    plt.xlabel('colleges', fontsize = 20)
    plt.title(figureName)
    plt.xticks(index, collegelist, fontsize=10)
    plt.yticks(fontsize=15)
    plt.savefig(r'C:\Users\54692\Desktop\EudemoniaSurfer-rec2020-master\rec2020\static\images\test.png',dpi = 400)


#以下函数通过本地测试
def QuestionsIntoAnswer11(request):               #**省*科**分冲一冲能上什么学校？
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')    #question/score/province/categry从前端传回

    #province = "江苏"
    #category = "理科"
    #score = 360

    #获得provinceid和categoryid
    provinceid = Provinces.objects.filter(provinceName = province)[0].provinceID
    categoryid = Category.objects.filter(categoryname = category)[0].categoryID

    AllCollegelist = Colleges.objects.filter().distinct()
    collegeMinScorelist = []
    collegelist = []
    for i in AllCollegelist:
        collegeid = i.collegeID
        collegescore = GetCollegeMinScore(collegeid, provinceid, categoryid, 2019)
        if (collegescore >= score and collegescore <= score + 20):
            collegeMinScorelist.append(collegescore)
            collegelist.append(i)


    #生成可视化图表
    collegeNameList = [i.collegeName for i in collegelist]
    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request,'KgInfoAnswers.html',
                  {'question':question, 'collegelist':collegelist, 'collegeMinScorelist':collegeMinScorelist})


def QuestionsIntoAnswer12(request):               #**省*科**分稳一稳能上什么学校？
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')  # question/score/province/categry从前端传回

    # 获得provinceid和categoryid
    provinceid = Provinces.objects.filter(provinceName=province)[0].provinceID
    categoryid = Category.objects.filter(categoryname=category)[0].categoryID

    AllCollegelist = Colleges.objects.filter().distinct()
    collegeMinScorelist = []
    collegelist = []
    for i in AllCollegelist:
        collegeid = i.collegeID
        collegescore = GetCollegeMinScore(collegeid, provinceid, categoryid, 2019)
        if (collegescore >= score - 10 and collegescore <= score + 10):
            collegeMinScorelist.append(collegescore)
            collegelist.append(i)

    #生成可视化图表
    collegeNameList = [i.collegeName for i in collegelist]
    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request, 'KgInfoAnswers.html',
                  {'question': question, 'collegelist': collegelist, 'collegeMinScorelist': collegeMinScorelist})

def QuestionsIntoAnswer13(request):               #**省*科**分保一保能上什么学校？
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')  # question/score/province/categry从前端传回

    # 获得provinceid和categoryid
    provinceid = Provinces.objects.filter(provinceName=province)[0].provinceID
    categoryid = Category.objects.filter(categoryname=category)[0].categoryID

    AllCollegelist = Colleges.objects.filter().distinct()
    collegeMinScorelist = []
    collegelist = []
    for i in AllCollegelist:
        collegeid = i.collegeID
        collegescore = GetCollegeMinScore(collegeid, provinceid, categoryid, 2019)
        if (collegescore >= score - 20 and collegescore <= score):
            collegeMinScorelist.append(collegescore)
            collegelist.append(i)

    #生成可视化图表
    collegeNameList = [i.collegeName for i in collegelist]
    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request, 'KgInfoAnswers.html',
                  {'question': question, 'collegelist': collegelist, 'collegeMinScorelist': collegeMinScorelist})

def QuestionsIntoAnswer14(request):               #**省*科**分能上什么/985学校/211学校/本科学校?
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')  # question/score/province/categry从前端传回

    # 获得provinceid和categoryid
    provinceid = Provinces.objects.filter(provinceName=province)[0].provinceID
    categoryid = Category.objects.filter(categoryname=category)[0].categoryID

    if(question.find("985") != -1):
        AllCollegelist = Colleges.objects.filter(project985=1).distinct()
    elif (question.find("211") != -1):
        AllCollegelist = Colleges.objects.filter(project211=1).distinct()
    else:
        AllCollegelist = Colleges.objects.filter().distinct()
    collegeMinScorelist = []
    collegelist = []
    for i in AllCollegelist:
        collegeid = i.collegeID
        collegescore = GetCollegeMinScore(collegeid, provinceid, categoryid, 2019)
        if (collegescore >= score - 15 and collegescore <= score + 15):
            collegeMinScorelist.append(collegescore)
            collegelist.append(i)

    #生成可视化图表
    collegeNameList = [i.collegeName for i in collegelist]
    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request, 'KgInfoAnswers.html',
                  {'question': question, 'collegelist': collegelist, 'collegeMinScorelist': collegeMinScorelist})


def QuestionsIntoAnswer21(request):               #**省*科**分冲一冲能上***省的什么学校？
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')
    tprovince = request.POST.get('Tprovince')     #Tprovince/question/score/province/categry从前端传回

    #获得provinceid、categoryid和tprovinceid
    provinceid = Provinces.objects.filter(provinceName = province)[0].provinceID
    categoryid = Category.objects.filter(categoryname = category)[0].categoryID
    tprovinceid = Provinces.objects.filter(provinceName = tprovince)[0].provinceID  #目标省份的id


    AllCollegelist = Colleges.objects.filter(provinceID_id = tprovinceid).distinct()
    collegeMinScorelist = []
    collegelist = []
    for i in AllCollegelist:
        collegeid = i.collegeID
        collegescore = GetCollegeMinScore(collegeid, provinceid, categoryid, 2019)
        if (collegescore >= score and collegescore <= score + 20):
            collegeMinScorelist.append(collegescore)
            collegelist.append(i)

    #生成可视化图表
    collegeNameList = [i.collegeName for i in collegelist]
    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request,'KgInfoAnswers.html',
                  {'question':question, 'collegelist':collegelist, 'collegeMinScorelist':collegeMinScorelist})

def QuestionsIntoAnswer22(request):               #**省*科**分稳一稳能上***省的什么学校？
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')
    tprovince = request.POST.get('Tprovince')      #Tprovince/question/score/province/categry从前端传回

    #获得provinceid、categoryid和tprovinceid
    provinceid = Provinces.objects.filter(provinceName = province)[0].provinceID
    categoryid = Category.objects.filter(categoryname = category)[0].categoryID
    tprovinceid = Provinces.objects.filter(provinceName = tprovince)[0].provinceID  #目标省份的id


    AllCollegelist = Colleges.objects.filter(provinceID_id = tprovinceid).distinct()
    collegeMinScorelist = []
    collegelist = []
    for i in AllCollegelist:
        collegeid = i.collegeID
        collegescore = GetCollegeMinScore(collegeid, provinceid, categoryid, 2019)
        if (collegescore >= score - 10 and collegescore <= score + 10):
            collegeMinScorelist.append(collegescore)
            collegelist.append(i)

    #生成可视化图表
    collegeNameList = [i.collegeName for i in collegelist]
    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request,'KgInfoAnswers.html',
                  {'question':question, 'collegelist':collegelist, 'collegeMinScorelist':collegeMinScorelist})

def QuestionsIntoAnswer23(request):               #**省*科**分保一保能上***省的什么学校？
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')
    tprovince = request.POST.get('Tprovince')      #Tprovince/question/score/province/categry从前端传回

    #获得provinceid、categoryid和tprovinceid
    provinceid = Provinces.objects.filter(provinceName = province)[0].provinceID
    categoryid = Category.objects.filter(categoryname = category)[0].categoryID
    tprovinceid = Provinces.objects.filter(provinceName = tprovince)[0].provinceID  #目标省份的id


    AllCollegelist = Colleges.objects.filter(provinceID_id = tprovinceid).distinct()
    collegeMinScorelist = []
    collegelist = []
    for i in AllCollegelist:
        collegeid = i.collegeID
        collegescore = GetCollegeMinScore(collegeid, provinceid, categoryid, 2019)
        if (collegescore >= score - 20 and collegescore <= score):
            collegeMinScorelist.append(collegescore)
            collegelist.append(i)

    #生成可视化图表
    collegeNameList = [i.collegeName for i in collegelist]
    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request,'KgInfoAnswers.html',
                  {'question':question, 'collegelist':collegelist, 'collegeMinScorelist':collegeMinScorelist})

def QuestionsIntoAnswer24(request):               #***省大学在**省**科分数线排名？
    question = request.POST.get('question')
    province = request.POST.get('province')
    tprovince = request.POST.get('Tprovince')
    category = request.POST.get('category')
    provinceid = Provinces.objects.filter(provinceName = province)[0].provinceID
    categoryid = Category.objects.filter(categoryname = category)[0].categoryID
    tprovinceid = Provinces.objects.filter(provinceName = tprovince)[0].provinceID  # 目标省份的id

    AllCollegelist = Colleges.objects.filter(provinceID_id = tprovinceid).distinct()
    collegeMinScorelist = []
    collegelist = []
    for i in AllCollegelist:
        collegeid = i.collegeID
        collegescore = GetCollegeMinScore(collegeid, provinceid, categoryid, 2019)
        collegeMinScorelist.append(collegescore)
        collegelist.append(i)

    #生成可视化图表
    collegeNameList = [i.collegeName for i in collegelist]
    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request,'KgInfoAnswers.html',
                  {'question':question, 'collegelist':collegelist, 'collegeMinScorelist':collegeMinScorelist})

def QuestionIntoAnswer25(request):                 #**省*科**分能上***省的什么/985学校/211学校/本科学校?
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')
    tprovince = request.POST.get('Tprovince')      #question/score/province/categry从前端传回
    # 获得provinceid和categoryid
    provinceid = Provinces.objects.filter(provinceName = province)[0].provinceID
    categoryid = Category.objects.filter(categoryname = category)[0].categoryID
    tprovinceid = Provinces.objects.filter(provinceName = tprovince)[0].provinceID  # 目标省份的id

    if(question.find("985") != -1):
        AllCollegelist = Colleges.objects.filter(project985=1, provinceID_id = tprovinceid).distinct()
    elif (question.find("211") != -1):
        AllCollegelist = Colleges.objects.filter(project211=1, provinceID_id = tprovinceid).distinct()
    else:
        AllCollegelist = Colleges.objects.filter(provinceID_id = tprovinceid).distinct()
    collegeMinScorelist = []
    collegelist = []
    for i in AllCollegelist:
        collegeid = i.collegeID
        collegescore = GetCollegeMinScore(collegeid, provinceid, categoryid, 2019)
        if (collegescore >= score - 15 and collegescore <= score + 15):
            collegeMinScorelist.append(collegescore)
            collegelist.append(i)

    #生成可视化图表
    collegeNameList = [i.collegeName for i in collegelist]
    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request, 'KgInfoAnswers.html',
                  {'question': question, 'collegelist': collegelist, 'collegeMinScorelist': collegeMinScorelist})


def QuestionIntoAnswer31(request):                  #**专业全国大学（在本省）录取分数线排名(2019)
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')
    tmajor = request.POST.get('Tmajor')      #question/score/province/categry/tmajor从前端传回,tmajor是目标一级学科

    provinceid = Provinces.objects.filter(provinceName = province)[0].provinceID
    categoryid = Category.objects.filter(categoryname = category)[0].categoryID

    tobjectslist = Majors.objects.filter(year = 2019, provinceID_id = provinceid, categoryID_id = categoryid).distinct()
    similaritylist = [getSimilarity(i.majorName, tmajor) for i in tobjectslist]
    targetlist = []
    for i in similaritylist:
        if i > 0.5:
            targetlist.append(tobjectslist[similaritylist.index[i]])

    collegelist = []
    collegeMinScorelist = []
    for i in targetlist:
        collegeObject = Colleges.objects.filter(collegeID = i.collegeID_id)[0]
        collegelist.append(collegeObject.collegeName)
        collegeMinScorelist.append(GetCollegeMinScore(i.collegeID_id, provinceid, categoryid, 2019))

    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request, 'KgInfoAnswers.html',
                  {'question': question, 'collegelist':collegelist})

def QuestionIntoAnswer32(request):                     #**省*科*分能上哪些学校的**专业？
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')
    tmajor = request.POST.get('Tmajor')      #question/score/province/categry/tmajor从前端传回,tmajor是目标一级学科
    provinceid = Provinces.objects.filter(provinceName = province)[0].provinceID
    categoryid = Category.objects.filter(categoryname = category)[0].categoryID

    tobjectslist = Majors.objects.filter(year = 2019, provinceID_id = provinceid, categoryID_id = categoryid).distinct()
    similaritylist = [getSimilarity(i.majorName, tmajor) for i in tobjectslist]
    targetlist = []
    for i in similaritylist:
        if i > 0.5:
            targetlist.append(tobjectslist[similaritylist.index[i]])

    collegelist = []
    collegeMinScorelist = []
    for i in targetlist:
        collegeObject = Colleges.objects.filter(collegeID = i.collegeID_id)[0]
        collegelist.append(collegeObject.collegeName)
        collegeMinScorelist.append(GetCollegeMinScore(i.collegeID_id, provinceid, categoryid, 2019))

    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request, 'KgInfoAnswers.html',
                  {'question': question, 'collegelist':collegelist})

def QuestionIntoAnswer41(request):                      #**专业***省的大学（在本省）录取分数线排名（2019）
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')
    tprovince = request.POST.get('Tprovince')
    tmajor = request.POST.get('Tmajor')      #question/score/province/categry/tmajor从前端传回,tmajor是目标一级学科
    provinceid = Provinces.objects.filter(provinceName = province)[0].provinceID
    categoryid = Category.objects.filter(categoryname = category)[0].categoryID
    tprovinceid = Provinces.objects.filter(provinceName = tprovince)[0].provinceID

    tobjectslist = Majors.objects.filter(year = 2019, provinceID_id = provinceid, categoryID_id = categoryid).distinct()
    similaritylist = [getSimilarity(i.majorName, tmajor) for i in tobjectslist]
    targetlist = []
    for i in similaritylist:
        if i > 0.5:
            targetlist.append(tobjectslist[similaritylist.index[i]])

    collegelist = []
    collegeMinScorelist = []
    for i in targetlist:
        collegeObject = Colleges.objects.filter(collegeID = i.collegeID_id)[0]
        if(collegeObject.provinceID_id == tprovinceid):
            collegelist.append(collegeObject.collegeName)
            collegeMinScorelist.append(GetCollegeMinScore(i.collegeID_id, provinceid, categoryid, 2019))

    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request, 'KgInfoAnswers.html',
                  {'question': question, 'collegelist':collegelist})

def QuestionIntoAnswer41(request):                      #**专业***省的大学（在本省）录取分数线排名（2019）
    question = request.POST.get('question')
    score = request.POST.get('score')
    province = request.POST.get('province')
    category = request.POST.get('category')
    tprovince = request.POST.get('Tprovince')
    tmajor = request.POST.get('Tmajor')               #question/score/province/categry/tmajor从前端传回,tmajor是目标一级学科
    provinceid = Provinces.objects.filter(provinceName = province)[0].provinceID
    categoryid = Category.objects.filter(categoryname = category)[0].categoryID
    tprovinceid = Provinces.objects.filter(provinceName = tprovince)[0].provinceID

    tobjectslist = Majors.objects.filter(year = 2019, provinceID_id = provinceid, categoryID_id = categoryid).distinct()
    similaritylist = [getSimilarity(i.majorName, tmajor) for i in tobjectslist]
    targetlist = []
    for i in similaritylist:
        if i > 0.5:
            targetlist.append(tobjectslist[similaritylist.index[i]])

    collegelist = []
    collegeMinScorelist = []
    for i in targetlist:
        collegeObject = Colleges.objects.filter(collegeID = i.collegeID_id)[0]
        if(collegeObject.provinceID_id == tprovinceid):
            collegelist.append(collegeObject.collegeName)
            collegeMinScorelist.append(GetCollegeMinScore(i.collegeID_id, provinceid, categoryid, 2019))

    VisualazationCollegeScore(collegelist, collegeMinScorelist, "")

    return render(request, 'KgInfoAnswers.html',
                  {'question': question, 'collegelist':collegelist})

#输入推荐学校，得到学校近三年的录取分数，录取位次和变化趋势
def getInfoOfUniv(college,pID,cID,major="all"):
    #参数为学校ID，省份ID（整数1-34），科类ID（整数1-3）
    scoreList=[]
    rankList=[]
    for _i in range(2017,2020):
        result1=Majors.objects.filter(collegeID=college,
                                provinceID=pID,
                                categoryID=cID,
                                year=_i,
                                majorName__contains=major,)   #模糊查询
        if(result1.exists()):
            score=result1[0].minScore
        else:
            score=0
        scoreList.append(score)
        result2=Rankings.objects.filter(score=score,
                                    provinceID=pID,
                                    categoryID=cID,
                                    year=_i,)
        if(result2.exists()):
            rank=result2[0].rank
        else:
            rank=0
        
        rankList.append(rank)
        
    return scoreList,rankList

def drawPicture(List,name):
    years=[2017,2018,2019]
    plt.xlabel('year')
    plt.ylabel(name)
    plt.plot(years,List,linewidth=3, color='b', marker='o',
         markerfacecolor='blue', markersize=5)
    
    x_major_locator=MultipleLocator(1)   #设置x坐标轴的坐标间隔为1
    ax=plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    for _, score in zip(years, List):
        plt.text(_, score, score, ha='center', va='bottom', fontsize=10)
    #将生成的图表返回到前端
    sio = BytesIO()
    plt.savefig(sio, format='png')
    data = base64.encodebytes(sio.getvalue()).decode()
    src = 'data:image/png;base64,' + str(data)
    plt.close()
    
    return src

def CollegeInfoGraphs(request):
    categoryDict={"文科":1,"理科":2,"综合":3}
    zeroList=[0,0,0]
    src1=drawPicture(zeroList,"score")
    src2=drawPicture(zeroList,"rank")
    if(request.method=="POST"):
        college = request.POST.get("college")
        category = request.POST.get("category")
        province=request.POST.get("province")
        provinceID=Provinces.objects.get(provinceName=province).provinceID
        collegeID=Colleges.objects.get(collegeName=college).collegeID
    
        scoreList,rankList=getInfoOfUniv(collegeID,provinceID,categoryDict[category])
        src1=drawPicture(scoreList,"score")
        src2=drawPicture(rankList,"rank")
        text1="图1：近三年"+college+"录取分数线变化"
        text2="图2：近三年"+college+"录取位次变化"
        return render(request,"CollegeInfoGraphs.html",{"src1":src1,"src2":src2,"text1":text1,"text2":text2})
    else:
        return render(request,"CollegeInfoGraphs.html",{"src1":src1,"src2":src2})


def MajorInfoGraphs(request):
    categoryDict={"文科":1,"理科":2,"综合":3}
    zeroList=[0,0,0]
    src1=drawPicture(zeroList,"score")
    src2=drawPicture(zeroList,"rank")
    if(request.method=="POST"):
        college = request.POST.get("college")
        category = request.POST.get("category")
        province=request.POST.get("province")
        majorName=request.POST.get("majorName")
        provinceID=Provinces.objects.get(provinceName=province).provinceID
        collegeID=Colleges.objects.get(collegeName=college).collegeID
    
        scoreList,rankList=getInfoOfUniv(collegeID,provinceID,categoryDict[category],majorName)
        src1=drawPicture(scoreList,"score")
        src2=drawPicture(rankList,"rank")
        text1="图1：近三年"+college+majorName+"专业录取分数线变化"
        text2="图2：近三年"+college+majorName+"专业录取位次变化"
        return render(request,"MajorInfoGraphs.html",{"src1":src1,"src2":src2,"text1":text1,"text2":text2})
    else:
        return render(request,"MajorInfoGraphs.html",{"src1":src1,"src2":src2})


#输入考生省份ID，展示本省及相邻省份的双一流院校
def getTopUnivOfNeighbors(pID):
    #存储相邻省份的字典
    Regions={1:[17,25,2,10,5,21,28,16],
             2:[17,25],
             3:[24,29],
             4:[16,28,13,9],
             5:[34,9,1,21,27,33,30,31],
             6:[30,33,15,20],
             7:[8,24,3],
             8:[7,24,3],
             9:[4,13],
             10:[1,34,17,25,2.5],
             11:[21,22,28,13,19,24],
             12:[34,23],
             13:[4,9,28,11,19],
             14:[27,22,29,32,33],
             15:[6,20,32,33,20],
             16:[17,25,2,1,4,9,28],
             17:[16,25,1,2,10,18,34],
             18:[23,34,17,25,2],
             19:[13,11,24,26],
             20:[30,15,6],
             21:[1,5,22,27,28,11],
             22:[11,14,21,27,14,29],
             23:[12,18,34],
             24:[19,11,22,29,3,7,8],
             25:[17,2],
             26:[19,24],
             27:[21,22,33,5,14],
             28:[4,16,13,9,1,21,11],
             29:[3,24,22,14,32],
             30:[34,31,5,33,6,20],
             31:[34,5,30],
             32:[33,14,29,15],
             33:[15,32,6,30,5,27,14],
             34:[30,31,5,10,17,25,2,18,23,12]}
    topDict={}
    Neighbors=Regions[pID]
    Neighbors.append(pID)
    for ID in Neighbors:
        pName=Provinces.objects.get(provinceID=ID).provinceName
        tops=Colleges.objects.filter(provinceID=ID,top=True)
        if(tops.exists()):
            topList=[]
            for top in tops:
                topList.append(top.collegeName)
            topDict[pName]=topList
        
    return topDict

def DisplayTopUnivOfNeighbors(request):
    if(request.method=="POST"):
        province=request.POST.get("province")
        provinceID=Provinces.objects.get(provinceName=province).provinceID
        
        topDict=getTopUnivOfNeighbors(provinceID)
        
        return render(request,"TopUnivOfNeighbors.html",{"topDict":topDict})
    else:
        return render(request,"TopUnivOfNeighbors.html")