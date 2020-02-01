
__all__ = ["createPandaJobs"]

from Gaugi import retrieve_kw, mkdir_p
from Gaugi.messenger import Logger
from Gaugi.messenger.macros import *
#from Gaugi.LoopingBounds import *

# A simple solution need to refine the documentation
from itertools import product
def create_iter(fun, n_items_per_job, items_lim):
  return ([fun(i, n_items_per_job)
           if (i+n_items_per_job) <= items_lim 
           else fun(i, items_lim % n_items_per_job) 
           for i in range(0, items_lim, n_items_per_job)])
  #return [fun(i, n_items_per_job) for i in range(0, items_lim, n_items_per_job)]

# default model (ringer vanilla)
# Remove the keras dependence and get keras from tensorflow 2.0
import tensorflow as tf
default_model = tf.keras.Sequential()
default_model.add(tf.keras.layers.Dense(5, input_shape=(100,), activation='tanh', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
default_model.add(tf.keras.layers.Dense(1, activation='linear', kernel_initializer='random_uniform', bias_initializer='random_uniform'))
default_model.add(tf.keras.layers.Activation('tanh'))
 


class CreatePandaJobs( Logger ):



  def __init__( self, **kw):

    Logger.__init__(self, **kw)



  @classmethod
  def _retrieveJobLoopingBoundsCol( cls, varBounds, varWindow ):
    """
      Create window bounded variables from larger range.
    """
    varIncr = varBounds.incr()
    jobWindowList = LoopingBoundsCollection()
    for jobTuple in varBounds.window( varWindow ):
      if len(jobTuple) == 1:
        jobWindowList += MatlabLoopingBounds(jobTuple[0], jobTuple[0])
      elif len(jobTuple) == 0:
        MSG_FATAL(self, "Retrieved empty window.")
      else:
        jobWindowList += MatlabLoopingBounds(jobTuple[0], 
                                             varIncr, 
                                             jobTuple[-1])
    return jobWindowList


  def time_stamp(self):
    from datetime import datetime
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y-%H.%M.%S")
    return timestampStr




  def __call__( self, **kw): 

    from sklearn.model_selection import KFold
    from saphyra import Norm1
    
    # Cross validation configuration
    outputFolder        = retrieve_kw( kw, 'outputFolder' ,       'jobConfig'           )
    sortBounds          = retrieve_kw( kw, 'sortBounds'   ,             5               )
    nInits              = retrieve_kw( kw, 'nInits'       ,             10              )
    nSortsPerJob        = retrieve_kw( kw, 'nSortsPerJob' ,             1               )
    nInitsPerJob        = retrieve_kw( kw, 'nInitsPerJob' ,             10              ) 
    nModelsPerJob       = retrieve_kw( kw, 'nModelsPerJob',             1               ) 
    models              = retrieve_kw( kw, 'models'       ,   [default_model]           )
    model_tags          = retrieve_kw( kw, 'model_tags'   ,   ['mlp_100_5_1']           )
    crossval            = retrieve_kw( kw, 'crossval'     , KFold(10,shuffle=True, random_state=512)  )
    ppChain             = retrieve_kw( kw, 'ppChain'      ,         [Norm1()]           )


    time_stamp = self.time_stamp()
    
    # creating the job mechanism file first

    mkdir_p(outputFolder)
    #mkdir_p(outputFolder+ '/job_container')
    
    if type(models) is not list:
      models = [models]
    
    #modelJobsWindowList = CreatePandaJobs._retrieveJobLoopingBoundsCol( PythonLoopingBounds( len(models) ), nModelsPerJob )
    #sortJobsWindowList  = CreatePandaJobs._retrieveJobLoopingBoundsCol( sortBounds                        , nSortsPerJob  )
    #initJobsWindowList  = CreatePandaJobs._retrieveJobLoopingBoundsCol( PythonLoopingBounds( nInits )     , nInitsPerJob  )
    print(len(models), sortBounds, nInits)
    modelJobsWindowList = create_iter(lambda i, sorts: list(range(i, i+sorts)), 
                                      nModelsPerJob,
                                      len(models))
    sortJobsWindowList  = create_iter(lambda i, sorts: list(range(i, i+sorts)), 
                                      nSortsPerJob,
                                      sortBounds)
    initJobsWindowList  = create_iter(lambda i, sorts: list(range(i, i+sorts)), 
                                      nInitsPerJob, 
                                      nInits)


    nJobs = 0 
    #for (models_list, sort_list, init_list) in product(modelJobsWindowList,
    for (model_idx_list, sort_list, init_list) in product(modelJobsWindowList,
                                                          sortJobsWindowList, 
                                                          initJobsWindowList):
      # This is need to fix. The problem is in Gaugi/python/messenger/macros.py
      # But it's works and create the jobs.
      MSG_INFO( self,
                'Creating job config with sort (%d to %d) and %d inits and model Index %d to %d', 
                sort_list[0], sort_list[-1], len(init_list), model_idx_list[0], model_idx_list[-1] )

      from saphyra.readers.versions import Job_v1
      job = Job_v1()
      # to be user by the database table
      job.setId( nJobs )
      job.setSorts(sort_list)
      job.setInits(init_list)
      job.setModels([models[idx] for idx in model_idx_list],  model_idx_list )
      #job.setModels(modelJobsWindowList[model_idx],  model )
      # save config file
      model_str = 'ml%i.mu%i' %(model_idx_list[0], model_idx_list[-1])
      sort_str  = 'sl%i.su%i' %(sort_list[0], sort_list[-1])
      init_str  = 'il%i.iu%i' %(init_list[0], init_list[-1])
      job.save( outputFolder+'/' + ('job_config.ID_%s.%s_%s_%s.%s') %
              ( str(nJobs).zfill(4), model_str, sort_str, init_str, time_stamp) )
      nJobs+=1

    MSG_INFO( self, "A total of %d jobs...", nJobs)

createPandaJobs = CreatePandaJobs()


