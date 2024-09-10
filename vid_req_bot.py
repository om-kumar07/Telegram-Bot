import re      #re-regular expression
import pyshorteners
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler,MessageHandler,filters,ContextTypes
import asyncio


tok_hash="Replace this text by your telegram bot token"  #telegram token will be pasted here



#insta post parameters
def download(post_link):
   data_json = instaloader.Instaloader(
    download_comments=False,
    download_geotags=False,
    download_pictures=False,
    download_video_thumbnails=False,
    download_videos=False,
    save_metadata=False,
    post_metadata_txt_pattern=''
    )
   links=post_link

   #exception block starts
   try:
    if(links.endswith('/') and  links.split('/')[-2]!='' and links.split('/')[-1]=='' 
       and (not links.split('/')[-2].startswith(tuple("0123456789"))) 
       and re.match(r'^[a-zA-Z0-9._]+$',links.split('/')[-2])
         and  len(links.split('/')[-2])<=30 and links.split('/')[-3]=="www.instagram.com" ):
      username=links.split('/')[-2]
      #print(username) used for prompting username 
      profile = instaloader.Profile.from_username(data_json.context, username)
      #print("debugging ,into the profile loop")      
      profile_pic_url = profile.profile_pic_url
      profile_pic_download_link = f"{profile_pic_url}?dl=1"
            
      #print(f"Profile picture download link: {profile_pic_download_link}")
      #print(f"Profile picture of {username} downloaded successfully.")
      return profile_pic_download_link
    
    link_tag=links.split('/')[-2]
    post_type = links.split('/')[-3] # it will access either p or reel

    post = instaloader.Post.from_shortcode(data_json.context,link_tag)
    data_json.download_post(post,target='')

    if(post_type=='p'):
       image_url = post.url
       image_download_link=f"{image_url}?dl=1"
       #print(image_download_link)
       #print(f"Instagram image downloaded successfully {links} and link_tag : {link_tag}\n")
       return image_download_link
    elif( post_type=='reel'):
       video_url = post.video_url
       video_download_link=f"{video_url}?dl=1"   
       #print(video_download_link)
       #print(f"\n Instagram video downloaded successfully {links} and link_tag : {link_tag}\n")
       return video_download_link
   
   except Exception as e:
    print(f"error occur {e}") 
    return -1  
   

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
   await update.message.reply_text("Welcome here, you can Download instagram videos or photos just paste the post link in message box") #first message promt to user

async def downloader(update:Update,context:ContextTypes.DEFAULT_TYPE):
   post_link=update.message.text  
   chat_id=update.message.chat_id
   EMOJI = "😄"

   await context.bot.send_chat_action(chat_id=chat_id, action='typing')
   if(post_link.startswith('https://www.instagram.com')):
    
      down_link=download(post_link)   #down_link simply accepts the download link of reel or photo or error(-1)


      if(down_link==-1):           #it will check either dead download link or not
         await update.message.reply_text("Something went wrong, either you paste currupted instagram link or wrong, check again!!")
      else:   
         short=pyshorteners.Shortener()
         down_link=short.tinyurl.short(down_link)
         print(f"shorten link {down_link} " )
         await update.message.reply_text(f"{down_link}")
         await asyncio.sleep(1)
         gif_url = 'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTB3dXZtZjV3YXZoenpnOG1ydGY1eHZpcDdweTh4MzFhamhmNDJlMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/YFQN3HFwusf5chR1XI/giphy.gif'
         await context.bot.send_animation(chat_id=chat_id, animation=gif_url)          #prompt gif to the user
         await update.message.reply_text(f"{EMOJI} Thank you for using our service")   #prompt message to the user 
         
   else:
      await update.message.reply_text("wrong link , please paste only instagram link ")
         



if __name__ =='__main__':
    application=ApplicationBuilder().token(tok_hash).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,downloader))
    application.run_polling()
