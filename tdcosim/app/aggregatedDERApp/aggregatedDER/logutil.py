import os
import json

from tdcosim.exceptionutil import ExceptionUtil


LogUtil=ExceptionUtil()
baseDir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logConfig={
	"logLevel": 20, 
	"logFilePath": os.path.join(baseDir,'logs','aggregatedderapp.log'), 
	"mode": "w", 
	"loggerName": "aggregatedderapp_logger"
}
LogUtil.create_logger(**logConfig)
