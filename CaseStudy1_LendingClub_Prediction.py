# -*- coding: utf-8 -*-
"""loan.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aom8Kdz0Zx87vS6ZYVpIb9soWP-uWJZ2
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
from google.colab import drive
import datetime as dt
drive.mount('/drive')
from sklearn.preprocessing import LabelEncoder 
import pickle
from sklearn.preprocessing import Normalizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn import metrics
import seaborn as sns
from matplotlib import rcParams
from scipy import stats
sns.color_palette("light:b", as_cmap=True)
import xgboost as xgb
# %matplotlib inline

df = pd.read_csv('/drive/My Drive/Colab Notebooks/loans_full_schema.csv')

df.head()

"""# **DATASET DESCRIPTION**

Lending Club is an online peer-to-peer credit marketplace that matches borrowers with investors. For evaluating the creditworthiness of theirborrowers, Lending Club relies on many factors related to borrowers such as credit history, employment, income, ratings, etc. The lending club then assigns rating/sub-rating to their borrowers based on their credit history. This rating information is then made available to investors who fund the loan requests and use this information to analyze loan requests and adjudicate the approved amount. In addition to the grade information, Lending Club provides historical loan performance data to investors for more comprehensive analysis. In short, our dataset contains a total of 10,000 records with 55 attributes in a comma-separated file. Each record in the file represents a loan request. This dataset has different types of features such as categorical, continuous, numerical, etc.

# **Issues With Dataset**
"""

df.describe()

df.shape

df.isna().sum()

df.columns[df.isnull().any()]

df[df['emp_title'].isna()]

(df['emp_title'].isna().sum()/df.shape[0])*100

df['emp_length'].value_counts(dropna=False)

df['emp_title'].value_counts(dropna=False)

df[df['annual_income_joint'].isnull()]

df[df['annual_income_joint'].isnull() & df['verification_income_joint'].isnull() & df['debt_to_income_joint'].isnull()]

df['annual_income_joint'].isnull().sum()

df['debt_to_income_joint'].isnull().sum()

df['verification_income_joint'].isnull().sum()

df['months_since_last_delinq'].isnull().sum()

df['months_since_90d_late'].isnull().sum()

df['months_since_last_credit_inquiry'].isnull().sum()

cat_features = ['emp_title','state', 'homeownership', 'verified_income','verification_income_joint','loan_purpose','application_type','grade','sub_grade' ,'loan_status','initial_listing_status','disbursement_method' ]

dat_features = ['issue_month','earliest_credit_line']

for col in df.columns:
    if col not in cat_features and col not in dat_features:
        q_low = df[col].quantile(0.01)
        q_hi  = df[col].quantile(0.99)
        dfo = df[(df[col] >= q_hi) & (df[col] <=q_low)]

dfo.head()

df['debt_to_income'].isnull().sum()

df['num_accounts_120d_past_due'].value_counts()

"""# **Summary:**



1.   Around 8.3% of observations contain missing data for emp_title and emp_length columns. We can assume that the customers in missing data could be students, retired, self-employed.
2.   85.45% of data doesn’t have data for attributes like annual_income_joint, debt_to_income_joint and verification_income_joint. We can assume that these customers haven’t had any joint accounts.
3.   We have 56.58% of the data with months_since_last_delinq attribute as null, 77.15% of data with months_since_90d_late as null and 12.71% of observations have months_since_last_credit_inquiry as null.
4.   Attribute num_accounts_120d_past_due have only one unique value throughout the dataset.
5.   We have 0.024% of data with debt_to_income as null.
6.   The data set has only 5 outlier records.

# **EDA & Pre-processing**
"""

df.head()

"""**Loan Status Distribution**"""

total = len(df)

plt.figure(figsize = (14,6))

g = sns.countplot(x="loan_status", data=df)
g.set_xticklabels(g.get_xticklabels(),rotation=45)
g.set_xlabel("Loan Status Categories", fontsize=12)
g.set_ylabel("Count", fontsize=15)
g.set_title("Loan Status Types Distribution", fontsize=20)
sizes=[]
for p in g.patches:
    height = p.get_height()
    sizes.append(height)
    g.text(p.get_x()+p.get_width()/2.,
            height + 3,
            '{:1.2f}%'.format(height/total*100),
            ha="center", fontsize=12) 

plt.show()

"""**Observations**


1.   The dataset has 93.75% of active customers, followed by 4.47% of Fully Paid customers.
2.   0.38% of customers had Late pay loan status.

**Loan Purpose**
"""

plt.figure(figsize=(14,6))

g = sns.countplot(x='loan_purpose', data=df)
g.set_title("Client Purposes for Loan Credit", fontsize=22)
g.set_xlabel("Purpose", fontsize=18)
g.set_ylabel('Count', fontsize=18)

sizes=[]

for p in g.patches:
    height = p.get_height()
    sizes.append(height)
    g.text(p.get_x()+p.get_width()/2.,
            height + 3,
            '{:1.2f}%'.format(height/total*100),
            ha="center", fontsize=14) 
    
g.set_ylim(0, max(sizes) * 1.10)
g.set_xticklabels(g.get_xticklabels(),
                  rotation=45)

plt.show()

"""**Observations**


1.   From the above bar plot, it is evident that the majority of the loans are due to debt consolidation and credit card bills.
2.   We can also observe that only 0.1% of people secured loans for renewable energy


"""

sns.color_palette("light:b", as_cmap=True)
df['int_round'] = df['interest_rate'].round(0).astype(int)
plt.figure(figsize = (12,16))

plt.subplot(311)
g1 = sns.boxplot(x="loan_status", y="int_round", data=df)
g1.set_xticklabels(g1.get_xticklabels(),rotation=45)
g1.set_xlabel("Loan Status Categories", fontsize=12)
g1.set_ylabel("Interest Rate Distribution", fontsize=15)
g1.set_title("Loan Status by Interest Rate", fontsize=20)

plt.subplot(312)
g2 = sns.boxplot(x="loan_status", y="loan_amount", data=df)
g2.set_xticklabels(g2.get_xticklabels(),rotation=45)
g2.set_xlabel("Loan Status Categories", fontsize=15)
g2.set_ylabel("Loan Amount Distribution", fontsize=15)
g2.set_title("Loan Status by Loan Amount", fontsize=20)

plt.subplots_adjust(hspace = 0.7,top = 0.9)
plt.show()

"""**Observations**


1.  Above box plots clearly state that the interest rates are high(16%) for the customers who pay late.
2.  The interest rate is low(around 10%) for the customers who had charged off.
3.  We can observe that the customers with Grace period and Current status received more loan amount of 15000 and charged off customers received less loan amount closer to $13000.

**Impact of Customer Grade**
"""

order_sub = df.groupby("sub_grade")['interest_rate'].count().index

plt.figure(figsize=(15,20))

plt.suptitle('Grade Distributions \n# Interest Rate and Loan Amount #', fontsize=22)

plt.subplot(311)
g = sns.boxplot(x="grade", y="loan_amount", data=df, hue="application_type", 
                order=["A",'B','C','D','E','F', 'G'])
g.set_xlabel("Grade Values", fontsize=17)
g.set_ylabel("Loan Amount", fontsize=17)
g.set_title("Lending Club Loan - Loan Amount Distribution by Grade", fontsize=20)
g.legend(loc='upper right')
plt.legend(loc=(1.02,0.8))

plt.subplot(312)
g1 = sns.boxplot(x='grade', y="interest_rate",data=df, 
               hue="application_type",  
               order=["A",'B','C','D','E','F', 'G'])
g1.set_xlabel("Grade Values", fontsize=17)
g1.set_ylabel("Interest Rate", fontsize=17)
g1.set_title("Lending Club Loan - Interest Rate Distribution by Grade", fontsize=20)
plt.legend(loc=(1.02,0.8))

plt.show()

"""**Observations**


1.   It is clearly evident that customers with Grade G will be approved with higher loan amounts of $36000 and they pay hight interest rate of 30.9%.
2.   Customers who falls under grade A, will given loan with very low intrest rates around 7.5%.
3.   Joint account customers have higher interset rates and higher loan amounts than individaul account holders.

## **Interest Rate Prediction**

**Feature** **Engineering**
"""

output =['interest_rate']

"""**Feature Division**"""

#Categorical Features
cat_features = ['emp_title','state', 'homeownership', 'verified_income','verification_income_joint','loan_purpose','application_type','grade','sub_grade' ,'loan_status','initial_listing_status','disbursement_method' ]
for col in cat_features:
  df[col]=df[col].fillna('Nan')

#Date Features
dat_features_mm_yy = ['issue_month']
dat_features_yy = ['earliest_credit_line'] 
dat_features = ['issue_month','earliest_credit_line']

#Valued Features
float_features= []
for col in df.columns:
  if col not in cat_features and col not in dat_features and col not in output:
    if df[col].nunique() > 1:
      
      float_features.append(col)
    else:
      del df[col]

"""**Zero Imputation**"""

for col in float_features:
  df[col]=df[col].fillna(0)

df.head()

"""**Label Encoding for categorical Attributes**"""

for col in cat_features:
  le = LabelEncoder()
  # print(df[col].head())
  df[col] = le.fit_transform(df[col])
  output = open(str(col)+'.pkl', 'wb')
  pickle.dump(le, output)
  output.close()

df.head()

"""Normalization"""

#Normalize float features
for col in float_features:
  # normalizer = Normalizer()
  # df[col] = normalizer.fit_transform(df[col])
  df[col]=(df[col]-df[col].min())/(df[col].max()-df[col].min())

df.head()

#Date Features
for col in dat_features:
  df[col] = pd.to_datetime(df[col])
  df[col]=df[col].map(dt.datetime.toordinal)

df.head()

"""**Train Test Split**"""

Y = df['interest_rate']
X = df.drop(['interest_rate'], axis = 1)
X_train, X_test, y_train, y_test = train_test_split(X,Y, test_size= 0.3, random_state = 5)

"""**Linear Regression Model**"""

lr = LinearRegression()
lr_model = lr.fit(X_train, y_train)

print(f'bias = {lr_model.intercept_}')
print(f'weights = {lr_model.coef_}')

"""**Testing**"""

y_pred = lr_model.predict(X_test)

"""**Model Evaluation**"""

print("Absolute Error: ",metrics.mean_absolute_error(y_test,y_pred))
print("Mean Square Error: ",metrics.mean_squared_error(y_test,y_pred))
print("Rooot Mean Square Error: ",np.sqrt(metrics.mean_squared_error(y_test,y_pred)))

plt.figure(figsize=(10,10))
plt.scatter(y_test, y_pred, c='orange')
plt.yscale('log')
plt.xscale('log')

p1 = max(max(y_pred), max(y_test))
p2 = min(min(y_pred), min(y_test))
plt.plot([p1, p2], [p1, p2], 'b-')
plt.xlabel('True Values', fontsize=15)
plt.ylabel('Predictions', fontsize=15)
plt.axis('equal')
plt.show()

"""**R Squared**"""

print("R Square :",metrics.r2_score(y_test,y_pred))

"""**XGBOOST Implementation**"""

xgb_model = xgb.XGBRegressor()
xgb_model.fit(X_train, y_train)

"""**Testing**"""

y_pred_xg = xgb_model.predict(X_test)

"""**Model Evalaution**"""

print("Absolute Error: ",metrics.mean_absolute_error(y_test,y_pred_xg))
print("Mean Square Error: ",metrics.mean_squared_error(y_test,y_pred_xg))
print("Rooot Mean Square Error: ",np.sqrt(metrics.mean_squared_error(y_test,y_pred_xg)))

"""**R Squared**"""

print("R Square :",metrics.r2_score(y_test,y_pred_xg))

"""# **Assumptions:**


1.   We assumed that the missing customers in emp_title and emp_length attributes could be students, retired, self-employed and we assigned a value to the missing data using a label encoder.
2.   85.45% of data doesn’t have data for attributes like annual_income_joint, debt_to_income_joint and verification_income_joint. We can assume that these customers haven’t had any joint accounts and we imputed them with 0 value.

3.   Columns such as months_since_last_delinq, months_since_90d_late, months_since_last_credit_inquiry, debt_to_income were imputed with 0 based on the assumption that these customers don’t pay late.
5.   We considered outliers assuming that the corresponding data is probable.

1.   If I had more time, I would have done univariate, bi-variate, and multi-variate analyses.
2.   I would have made sure to use only some of the attributes rather than everything in the dataset.
3.   Nevertheless, I secured an R-square score of .99 which I believe had done the job well.
"""