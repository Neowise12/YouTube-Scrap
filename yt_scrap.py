#%%
from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns
import matplotlib as plt

api_key='AIzaSyB-0DxFBjNUVFLFEa2YxkoaZH_OCRWeiaY'
channel_id='UCnz-ZXXER4jOvuED5trXfEA'
all_data=[]

channel_ids=['UCnz-ZXXER4jOvuED5trXfEA',
             'UCeVMnSShP_Iviwkknt83cww',
             'UCJskGeByzRRSvmOyZOz61ig',
             'UCh9nVJoWXmFb7sLApWGcLPQ',
             'UCcIXc5mJsHVYTZR1maL5l9w'

]
youtube = build('youtube','v3',developerKey= api_key)

def get_channel_stats(youtube,channel_ids):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    ) 
    

    respose =request.execute()
    for i in range(len(respose['items'])):
        data= dict(channel_name= respose['items'][i]['snippet']['title'],
                   Suscribers=respose['items'][i]['statistics']['subscriberCount'],
                   views=respose['items'][i]['statistics']['viewCount'],
                   total_videos =respose['items'][i]['statistics']['videoCount'],
                   playlist_id=respose['items'][i]['contentDetails']['relatedPlaylists']['uploads']
                
                
                   )
        all_data.append(data)
    return all_data

channel_statistics=  get_channel_stats(youtube,channel_ids)

channel_data=pd.DataFrame(channel_statistics)
channel_data['Suscribers']=pd.to_numeric(channel_data['Suscribers'])
channel_data['views']=pd.to_numeric(channel_data['views'])
channel_data['total_videos']=pd.to_numeric(channel_data['total_videos'])

playlist_id= channel_data.loc[channel_data['channel_name']=='CodeWithHarry','playlist_id'].iloc[0]

# print(channel_data.dtypes)
# print(channel_data)
# sns.set(rc={'figure.figsize':(10,8)})
# ax= sns.barplot(x='channel_name',y='Suscribers',data=channel_data)
video_ids=[]
def get_video_ids(youtube,playlist_id):
    request=youtube.playlistItems().list(
        part='contentDetails',playlistId=playlist_id,
        maxResults=50)
    respose= request.execute()
    
    for i in range(len(respose['items'])):
        video_ids.append(respose['items'][i]['contentDetails']['videoId'])

    next_page_token= respose.get('nextPageToken')
    more_pages= True

    while more_pages:
        if next_page_token is None:
            more_pages= False
        else:
            request= youtube.playlistItems().list(

                part='contentDetails',
                playlistId= playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )   
            respose= request.execute() 
            for i in range(len(respose['items'])):
                video_ids.append(respose['items'][i]['contentDetails']['videoId'])
            next_page_token=respose.get('nextPageToken')    

    
    return video_ids


def get_video_details(youtube,video_ids):

    all_video_stats=[]
    for i in range(0,len(video_ids),50):
        request= youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i+50]))

        respose = request.execute()

        # return respose
        for video in respose['items']:
            video_stats=dict(Title=video['snippet']['title'],
                             published_at=video['snippet']['publishedAt'],
                             views=video['statistics']['viewCount'],
                             likes=video['statistics']['likeCount'],
                             comments=video['statistics']['commentCount']                 

            )
            all_video_stats.append(video_stats)
    return all_video_stats



get_video_ids(youtube,playlist_id)
video_details =get_video_details(youtube,video_ids)
video_data=pd.DataFrame(video_details)
video_data['published_at'] = pd.to_datetime(video_data['published_at']).dt.date


video_data['views']=pd.to_numeric(video_data['views'])
video_data['likes']=pd.to_numeric(video_data['likes'])
video_data['comments']=pd.to_numeric(video_data['comments'])

top10= video_data.sort_values(by='views',ascending=False).head(10)

# ax1= sns.barplot(x='views',y='Title',data=top10)

video_data['Month']=pd.to_datetime(video_data['published_at']).dt.strftime('%b')


# videos_per_month= video_data.groupby('Month',as_index=False).size()
# videos_per_month

# sort_order=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
# videos_per_month.index=pd.CategoricalIndex(videos_per_month['Month'],categories=sort_order,ordered=True)
# videos_per_month.sort_index()

videos_per_month = video_data.groupby('Month').size().reset_index(name='size')

sort_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
videos_per_month['Month'] = pd.Categorical(videos_per_month['Month'], categories=sort_order, ordered=True)
videos_per_month = videos_per_month.sort_values(by='Month')

videos_per_month = videos_per_month.reset_index(drop=True)

ax2= sns.barplot(x='Month',y='size',data= videos_per_month)
video_data.to_csv('Code with harry videos analysis.csv')

#%%