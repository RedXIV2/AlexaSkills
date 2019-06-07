# -*- coding: utf-8 -*-
"""Simple fact sample app."""

import random
import logging
import boto3
import json
import decimal
from collections import defaultdict

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response


# =========================================================================================================================================
# TODO: The items below this comment need your attention.
# =========================================================================================================================================
SKILL_NAME = "Family Jobs"
GET_FACT_MESSAGE = "Here's the list of chores: "
HELP_MESSAGE = "You can say list jobs for the kids, or, you can say exit... What can I help you with?"
HELP_REPROMPT = "What up my lord?"
STOP_MESSAGE = "Toodles!"
FALLBACK_MESSAGE = "You have not asked this correctly. Stop avoiding work and ask for your jobs. Or will we just ground you now?"
FALLBACK_REPROMPT = 'What can I help you with?'
EXCEPTION_MESSAGE = "Why are you trying to fry my circuts?"

# =========================================================================================================================================
# Code used to get data from DynamoDB for parsing
# =========================================================================================================================================

def getRandomChore(listOfChores, countOfJobs, targetKid):
    jobNotAllocated = True
    print("I should only be seen once")
    while jobNotAllocated:
        print(jobNotAllocated)
        TodaysChoreID = random.randint(1,countOfJobs)
        TodaysChoreCorrupt = listOfChores[str(TodaysChoreID)]
        print(TodaysChoreCorrupt)
        TodaysChore = ChoreToDict(TodaysChoreCorrupt)
        if TodaysChore[targetKid] == True:
            jobNotAllocated = False
            print(jobNotAllocated)
    return TodaysChore


def ChoreToDict(choreAsAList):
    ChoreAsBadStr = str(choreAsAList)
    ChoreAsStr = ChoreAsBadStr[2:-2]
    ChoreAsADict = json.loads(ChoreAsStr)
    return ChoreAsADict


def dynamodbResponse():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('chores')
    pe = "JobID, JobName, Lewis, Rebecca, Jacob, Isabelle"
    response = table.scan(ProjectionExpression=pe)
    return response


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def getChores():
    response = dynamodbResponse()
    resultDict = defaultdict(list)
    jobCounter = 0
    for i in response['Items']:
        jobCounter = jobCounter + 1
        dictRecord = json.dumps(i, cls=DecimalEncoder)
        jsonOutput = json.loads(dictRecord)
        resultDict[jsonOutput['JobID']].append(json.dumps(i, cls=DecimalEncoder))
    LewisChore = getRandomChore(resultDict,jobCounter, "Lewis")
    RebeccaChore = getRandomChore(resultDict,jobCounter, "Rebecca")
    JacobChore = getRandomChore(resultDict,jobCounter, "Jacob")
    IzzyChore = getRandomChore(resultDict,jobCounter, "Isabelle")
    LewisMsg = "Lewis, You will " + LewisChore["JobName"] + ". "
    BexMsg = "Rebecca, You will " + RebeccaChore["JobName"] + ". "
    JacobMsg = "Jacob, You will " + JacobChore["JobName"] + ". "
    IzzyMsg = "Izzy, You will " + IzzyChore["JobName"] + "."
    SayThis = LewisMsg + BexMsg + JacobMsg + IzzyMsg
    return SayThis


# =========================================================================================================================================
# Editing anything below this line might break your skill.
# =========================================================================================================================================

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Built-in Intent Handlers
class GetNewFactHandler(AbstractRequestHandler):
    """Handler for Skill Launch and GetNewFact Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("LaunchRequest")(handler_input) or
                is_intent_name("get_jobs_for_all")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In GetNewFactHandler")

        SayThis = getChores()
        speech = GET_FACT_MESSAGE + SayThis

        handler_input.response_builder.speak(speech).set_should_end_session(True).set_card(
            SimpleCard(SKILL_NAME, SayThis))
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(
                SKILL_NAME, HELP_MESSAGE))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(STOP_MESSAGE)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent.
    AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        handler_input.response_builder.speak(FALLBACK_MESSAGE).ask(
            FALLBACK_REPROMPT)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(
            HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(GetNewFactHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# TODO: Uncomment the following lines of code for request, response logs.
# sb.add_global_request_interceptor(RequestLogger())
# sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()