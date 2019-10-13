__all__ = ['tableBoardParser']

from Gaugi import ArgumentParser, BooleanStr, NotSet

################################################################################
# Create cross valid monitoring job parser file related objects
################################################################################

def TableBoardParser():
  tparser = ArgumentParser(add_help = False, 
                                          description = 'Retrieve table board information performance.',
                                          conflict_handler = 'resolve')
  reqArgs = tparser.add_argument_group( "required arguments", "")
  reqArgs.add_argument('-f', '--file', action='store', required = True,
                       help = """The crossvalidation data files or folders that will be used to run the
                                 analysis.""")
  reqArgs.add_argument('-d','--dataPath', default = None, required = True,
                       help = """The tuning data file to retrieve the patterns.""")
  #reqArgs = crossValStatsMonParser.add_argument_group( "optional arguments", "")
  reqArgs.add_argument('--debug', default=False, type=BooleanStr,
                       help = "Debug mode")
  reqArgs.add_argument('--grid', default=False, type=BooleanStr,
                       help = "Enable the grid filter tag.")
  reqArgs.add_argument('--doBeamer', default=False, type=BooleanStr,
                       help = "Enable the beamer creation.")
  reqArgs.add_argument('--reference', default=None,
                       help = "The reference string to be used.")
  reqArgs.add_argument('--output', '-o', default="report", 
                       help = "the output file path to the data"
                       )
  reqArgs.add_argument('--choicesfile', '-c', default=None, 
                       help = "the .mat file with the neuron choices "
                       )
  return tparser


tableBoardParser = TableBoardParser()
