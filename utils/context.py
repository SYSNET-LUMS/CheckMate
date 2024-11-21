from utils.utils import getNodeParent
from config.config import (
    GIVE_FORMAT_EXAMPLES,
    GIVE_LOOP_PERF_EXMAPLES
)
from config.globals import (
    GLOBAL_CONTEXT,
    LOOP_PERF_EXAMPLES,
    APPROXIMATION_FORMAT_EXAMPLES,
    CHAT_HISTORY,
    CODE_BASE_SUMMARY,
)

def manufacturerContext(PDG, this_function): #Cat 6

    global APPROXIMATION_FORMAT_EXAMPLES
    global CHAT_HISTORY
    global GIVE_FORMAT_EXAMPLES

    parent_entities = getNodeParent(this_function, PDG)
    
    parent_context = getConversationHistory(parent_entities, CHAT_HISTORY)
    
    this_context = GLOBAL_CONTEXT.copy()
    
    if GIVE_LOOP_PERF_EXMAPLES:
        this_context += LOOP_PERF_EXAMPLES
    if GIVE_FORMAT_EXAMPLES:
        this_context += APPROXIMATION_FORMAT_EXAMPLES
    if CODE_BASE_SUMMARY != []:
        this_context += CODE_BASE_SUMMARY


    this_context +=  parent_context
    return this_context

def getConversationHistory(function_list, chat_history): #Cat 6
    manufactured_history = []
    for function in function_list:
        try:
            manufactured_history += chat_history[function]
        except:
            print("A converstation that does not exist was attempted to be added: ", function)
            continue

    return manufactured_history