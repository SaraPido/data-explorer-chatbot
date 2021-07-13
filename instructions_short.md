**Requisiti ed esecuzione chatbot**

- Do the dump (schema + data) of the mysql database
- Save it in the folder 'resources/db'
- To create the files 'db_concept' and 'db_schema':
  - modify the file modules/database/parser.py such that it contains the name of the db and the correct letter for the names of the db files (e.g. db_concept_f.json)
        
        cd modules/database
        python -m parser
        cd ../..
        
- Modify the two created files according to the data of your interest (for example in category you can put the columns that you want to group by)

**Train the model**
- Change the file 'settings.py': put the name of the db of interest and the correct data such as 
        
        'virus' : ['d', 'virus', '1046778538:AAF2CKzjxwzCu9fiDLgadBujYKuBKhgKmdE']
 
  where 'f' is the letter used to save the db files, 'virus' is the name of the db and the last one is the key to use for Telegram (for now we skipped it)

- To generate the file chatito_model:
        
        python -m modules.translator
  
- To generate the training and testing files for Rasa:
        
        cd writer && npx chatito chatito_model.chatito --format=rasa --defaultDistribution=even
  
- To train the model:
        
        cd .. && python -m modules.trainer

**Launch the app**
- To launch the app at 0.0.0.0:5080
        
        python -m run
        
        