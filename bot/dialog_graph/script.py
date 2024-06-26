from dff.script import RESPONSE, TRANSITIONS, GLOBAL, LOCAL, PRE_TRANSITIONS_PROCESSING
from dff.script import labels as lbl
import dff.script.conditions as cnd
from dff.script.core.message import Button
from dff.messengers.telegram import (
    telegram_condition,
    TelegramMessage,
    RemoveKeyboard,
    TelegramUI)
from bot.dialog_graph.processing import del_slot, change_flag, test_answer_processing, clear_intents
from bot.dialog_graph.response import (gigacht_response, nice_t_meet_u_response, say_hi_response, \
                                       mentor_query_response, question_unsuccess_node, mentor_name_response,
                                       email_response, qa_response, test_start_response,
                                       success_form_response, are_u_sure_nod_response,
                                       training_session_response, generate_progress_response,
                                       process_test_response, result_node_response)
from bot.dialog_graph.conditions import is_slots_filled, is_intent_match, is_name_exist, is_flag_true
from bot.dialog_graph.consts import PERSONAL_INFO, NAME, FORM, QUESTION, CODE, EMAIL, DATE, TEST_FLAG

script = {
    GLOBAL: {
        TRANSITIONS: {('general_flow', 'say_hi_node'): cnd.exact_match(TelegramMessage('/start')),
                      ('dff_flow', 'check_progress_node'): cnd.exact_match(TelegramMessage('Прогресс')),
                      ('dff_flow', 'test_node_start'): cnd.exact_match(TelegramMessage('Пройти тест')),
                      ('general_flow', "tell_about_bot_node"): is_intent_match(['tell_about_bot']),
                      ('form_flow', 'mentor_query_node'): is_intent_match(['mentor_query']),
                      ('general_flow', "smth_else_node"): is_intent_match(['action_cancle']),
                      ('dff_flow', 'qa_session_node'): is_intent_match(['qa_framework_info']),
                      ('dff_flow', 'training_session_node'): is_intent_match(['training_session']), }
    },
    'general_flow': {
        "start_node": {
            RESPONSE: TelegramMessage(),
            TRANSITIONS: {('general_flow', 'say_hi_node'): telegram_condition(commands=["start", "restart"])},
            PRE_TRANSITIONS_PROCESSING: {
                "1": clear_intents()
            }
        },

        "say_hi_node": {
            RESPONSE: say_hi_response,
            TRANSITIONS: {lbl.repeat(): cnd.negation(is_slots_filled(PERSONAL_INFO, NAME)),
                          ('general_flow', 'ntmu_node'): is_slots_filled(PERSONAL_INFO, NAME)}
        },

        "chitchat_node": {
            RESPONSE: gigacht_response
        },

        "ntmu_node": {
            RESPONSE: nice_t_meet_u_response
        },

        "tell_about_bot_node": {
            RESPONSE: gigacht_response
        },
        "smth_else_node": {
            RESPONSE: TelegramMessage('Как я могу помочь вам сейчас?', ui=TelegramUI(
                buttons=[
                    Button(text="Прогресс"),
                    Button(text="Пройти тест"),
                ],
                is_inline=False,
                row_width=4))
        }
    },

    "form_flow": {
        LOCAL: {
            TRANSITIONS: {
                ('form_flow', 'mentor_query_node'): cnd.negation(
                    cnd.any([is_slots_filled(FORM, QUESTION), is_slots_filled(FORM, CODE)])),
                ('form_flow', 'mentor_name_node'): cnd.negation(is_slots_filled(FORM, NAME)),
                ('form_flow', 'email_node'): cnd.negation(is_slots_filled(PERSONAL_INFO, EMAIL)),
                ('form_flow', 'date_node'): cnd.negation(is_slots_filled(PERSONAL_INFO, DATE)),
            }
        },
        'mentor_query_node': {
            RESPONSE: mentor_query_response,
            TRANSITIONS: {
                ('form_flow', 'are_u_sure_node'): is_intent_match(['action_cancle']),
                lbl.repeat(): cnd.negation(cnd.any([is_slots_filled(FORM, QUESTION),
                                                    is_slots_filled(FORM, CODE),
                                                    telegram_condition(
                                                        func=lambda message: (
                                                                message.document and
                                                                message.document.file_name.endswith(".py")
                                                        ),
                                                        content_types=["document"],
                                                    )
                                                    ])),
                ('form_flow', 'question_unsuccess_node'): cnd.exact_match(TelegramMessage(text='Нет')),
                ('form_flow', 'mentor_name_node'): cnd.any(
                    [cnd.exact_match(TelegramMessage(text='Да')), cnd.negation(is_slots_filled(FORM, NAME))]),
                ('form_flow', 'email_node'): cnd.any(
                    [cnd.exact_match(TelegramMessage(text='Да')), cnd.negation(is_slots_filled(PERSONAL_INFO, EMAIL))]),
                ('form_flow', 'date_node'): cnd.any(
                    [cnd.exact_match(TelegramMessage(text='Да')), cnd.negation(is_slots_filled(PERSONAL_INFO, DATE))])
            }
        },
        'question_unsuccess_node': {
            RESPONSE: question_unsuccess_node,
            TRANSITIONS: {
                lbl.repeat(): cnd.negation(cnd.any([is_slots_filled(FORM, QUESTION),
                                                    is_slots_filled(FORM, CODE),
                                                    telegram_condition(
                                                        func=lambda message: (
                                                                message.document and
                                                                message.document.file_name.endswith(".py")
                                                        ),
                                                        content_types=["document"],
                                                    )
                                                    ])),
                ('form_flow', 'are_u_sure_node'): is_intent_match(['action_cancle'])
            }
        },

        'mentor_name_node': {
            RESPONSE: mentor_name_response,
            TRANSITIONS: {
                ('form_flow', 'are_u_sure_node'): is_intent_match(['action_cancle']),
                lbl.repeat(): cnd.negation(is_slots_filled(FORM, NAME)),
                ('form_flow', 'wrong_name_node'): cnd.all([is_slots_filled(FORM, NAME), cnd.negation(is_name_exist())]),
            }
        },

        'wrong_name_node': {
            RESPONSE: TelegramMessage(
                text='К сожалению, среди наших менторов в настоящий момент нет никого с таким именем. '
                     'Пожалуйста, выберите кого-нибудь из списка доступных менторов.'),
            TRANSITIONS: {
                ('form_flow', 'are_u_sure_node'): is_intent_match(['action_cancle']),
                lbl.repeat(): cnd.any([cnd.negation(is_slots_filled(FORM, NAME)), cnd.negation(
                    cnd.all([is_slots_filled(FORM, NAME), cnd.negation(is_name_exist())]))]),
            }
        },

        'email_node': {
            RESPONSE: email_response,
            TRANSITIONS: {
                ('form_flow', 'are_u_sure_node'): is_intent_match(['action_cancle']),
                lbl.repeat(): cnd.negation(is_slots_filled(PERSONAL_INFO, EMAIL)),
                ('form_flow', 'unsuccess_email_node'): cnd.exact_match(TelegramMessage(text='Нет'))
            },
            PRE_TRANSITIONS_PROCESSING: {"1": del_slot(PERSONAL_INFO, EMAIL, True)}
        },

        'unsuccess_email_node': {
            RESPONSE: TelegramMessage(**{"text": "Пожалуйста, введите почту еще раз", "ui": RemoveKeyboard()}),
            TRANSITIONS: {
                ('form_flow', 'are_u_sure_node'): is_intent_match(['action_cancle']),
                lbl.repeat(): cnd.negation(is_slots_filled(PERSONAL_INFO, EMAIL)),
                ('form_flow', 'email_node'): cnd.true()
            }
        },

        'date_node': {
            RESPONSE: TelegramMessage(
                text='Пожалуйста, укажите, дату и месяу, когда вы свободны. Ментор напишет вам, и вы договоритесь о встрече',
                ui=RemoveKeyboard()),
            TRANSITIONS: {
                ('form_flow', 'are_u_sure_node'): is_intent_match(['action_cancle']),
                lbl.repeat(): cnd.negation(is_slots_filled(FORM, DATE)),
                ('form_flow', 'success_node'): cnd.any(
                    [is_slots_filled(FORM, NAME), is_slots_filled(PERSONAL_INFO, EMAIL),
                     is_slots_filled(PERSONAL_INFO, DATE)])
            }
        },

        'success_node': {
            RESPONSE: success_form_response,
            PRE_TRANSITIONS_PROCESSING: {"1": del_slot(FORM, DATE, False),
                                         "2": del_slot(FORM, NAME, False),
                                         "3": del_slot(FORM, QUESTION, False),
                                         "4": del_slot(FORM, CODE, False)},
            TRANSITIONS: {('general_flow', 'say_hi_node'): cnd.exact_match(TelegramMessage('/start')),
                          ('dff_flow', 'check_progress_node'): cnd.exact_match(TelegramMessage('Прогресс')),
                          ('dff_flow', 'test_node_start'): cnd.exact_match(TelegramMessage('Пройти тест')),
                          ('general_flow', "tell_about_bot_node"): is_intent_match(['tell_about_bot']),
                          ('form_flow', 'mentor_query_node'): is_intent_match(['mentor_query']),
                          ('general_flow', "smth_else_node"): is_intent_match(['action_cancle']),
                          ('dff_flow', 'qa_session_node'): is_intent_match(['qa_framework_info']),
                          ('dff_flow', 'training_session_node'): is_intent_match(['training_session']),
                          ('general_flow', 'chitchat_node'): is_intent_match(['out_of_scope'])}
        },
        'are_u_sure_node': {
            RESPONSE: are_u_sure_nod_response,
            TRANSITIONS: {
                ('general_flow', 'smth_else_node'): cnd.exact_match(TelegramMessage('Да'))
            },
            PRE_TRANSITIONS_PROCESSING: {"1": del_slot(FORM, DATE, False),
                                         "2": del_slot(FORM, NAME, False),
                                         "3": del_slot(FORM, QUESTION, False),
                                         "4": del_slot(FORM, CODE, False)}
        }
    },

    'dff_flow': {
        'qa_session_node': {
            RESPONSE: qa_response
        },

        'training_session_node': {
            RESPONSE: training_session_response,
            TRANSITIONS: {
                ('dff_flow', 'training_session_node'): cnd.exact_match(TelegramMessage('Дальше')),
                ('general_flow', 'smth_else_node'): cnd.exact_match(TelegramMessage('Закончить обучение'))
            }
        },

        'check_progress_node': {
            RESPONSE: generate_progress_response
        },

        'test_node_start': {
            RESPONSE: test_start_response,
            TRANSITIONS: {
                ('dff_flow', 'test_node_process'): cnd.true()
            },
            PRE_TRANSITIONS_PROCESSING: {"1": change_flag(TEST_FLAG, True)}
        },
        'test_node_process': {
            RESPONSE: process_test_response,
            TRANSITIONS: {
                lbl.repeat(): is_flag_true(TEST_FLAG),
                ('dff_flow', 'result_node'): cnd.negation(is_flag_true(TEST_FLAG))
            },
            PRE_TRANSITIONS_PROCESSING: {'1': test_answer_processing()}
        },
        'result_node': {
            RESPONSE: result_node_response,
            PRE_TRANSITIONS_PROCESSING: {
                "1": del_slot('test', 'test_info', False),
                "2": del_slot('test', 'user_answers', False),
                "3": del_slot('test', 'test_answers', False),
            }
        }
    },
}
