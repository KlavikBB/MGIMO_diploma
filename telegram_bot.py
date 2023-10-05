from joblib import load

import pandas as pd

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from const import COLUMNS_FOR_TG, TOKEN, NUMERIC

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

lgbm_model = load('lgbm_model.joblib')
scaler = load('scaler.joblib')

filtered_df = pd.read_csv('norm_data.csv')
test_df = pd.read_csv('test.csv').iloc[[0]].drop('price', axis=1)  # DataFrame со всеми необходимыми столбцами

question_choices = {
    'flat_type': list(filtered_df['flat_type'].unique()),
    'rooms': sorted(list(filtered_df['rooms'].unique())),
    'rooms_type': list(filtered_df['rooms_type'].unique()),
    'bathroom': list(filtered_df['bathroom'].unique()),
    'renovation': list(filtered_df['renovation'].unique()),
    'building_type': list(filtered_df['building_type'].unique()),
    'finishing': list(filtered_df['finishing'].unique()),
    'house_type': list(filtered_df['house_type'].unique())
}

locality_data = pd.DataFrame(filtered_df.groupby(by='locality_name').count()['max_floor'].sort_values(ascending=False))

question_choices_2 = {
    'underground_nearest': sorted(list(filtered_df['underground_nearest'].unique())),
    'locality_name': sorted(list(locality_data[locality_data['max_floor'] > 46].index))
}

answers = {}  # Словарь для хранения ответов


class QuestionnaireStates(StatesGroup):
    ANSWERING = State()


@dp.message_handler(Command("start"))
async def start(message: types.Message):
    await message.answer("Добро пожаловать к предсказателю! Этот бот дает приблизительную цену квартиры в Москве "
                         "на основе полученных характеристик. Вариант 'unknown' в ответах означате 'не указано' или "
                         "'не знаю'. Перезапускать бота можно сколько угодно раз с помощью команды /start, но только "
                         "после завершения анкеты, так что если ввели высоту потолков равную 280 метрам, "
                         "ничего страшного. "
                         "Структура анкеты будет следующей: сначала вопросы о численных характеристиках квартиры, а "
                         "далее будут даваться вопросы, ответы на которые доступны из списка. Удачи!"
                         "\n\nВведите /begin, чтобы начать.")


@dp.message_handler(Command("begin"))
async def begin_questionnaire(message: types.Message, state: FSMContext):
    await message.answer("Приступаем к анкете. Ответьте на следующие вопросы:")

    data = await state.get_data()
    if "questions" not in data:
        await state.update_data(questions=list(COLUMNS_FOR_TG.keys()))

    await ask_next_question(message, state)


async def ask_next_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get("questions")

    if questions:
        current_question = questions[0]

        if current_question.split()[0] in question_choices:
            choices = question_choices[current_question.split()[0]]
            kb = [[KeyboardButton(text=f"{choice}") for choice in choices]]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            await message.answer("Пожалуйста, выберите вариант из списка (Внимание! На выбор должно предлагаться "
                                 "несколько вариантов)", reply_markup=keyboard)

        elif current_question.split()[0] == 'underground_nearest' or current_question.split()[0] == 'locality_name':

            # Создаем разметку клавиатуры с помощью кнопок
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            for option in question_choices_2[current_question.split()[0]]:
                keyboard.add(KeyboardButton(option))

            await message.answer("Пожалуйста, выберите вариант из списка (Внимание! На выбор должно предлагаться "
                                 "несколько вариантов)", reply_markup=keyboard)

        else:
            await message.answer('Пожалуйста, введите свое значение. ЧИСЛО:')

        await message.answer(current_question)

        await QuestionnaireStates.ANSWERING.set()
        await state.update_data(current_question=current_question)
    else:
        await message.answer("Больше вопросов нет. Считаем...")

        # Обрабатываем собранные ответы

        pred_df = pd.DataFrame(answers, index=[0])
        for i in pred_df.columns:
            print(i, pred_df[i])
            print()
        pred_df = pd.get_dummies(pred_df)
        pred = pd.concat([test_df, pred_df]).fillna(False).drop(
            pd.concat([test_df, pred_df]).drop(test_df.columns, axis=1),
            axis=1).iloc[[1]]
        pred[NUMERIC] = scaler.transform(pred[NUMERIC])
        pred.replace('False', 0)
        pred = pred.replace(False, 0)
        for i in pred.columns:
            print(i, pred[i])
            print()
        await message.answer(f'Приблизительная цена квартиры: {lgbm_model.predict(pred)[0]:.2f} рублей\n '
                             f'Хотите повторить? /start')

        # Сбросываем состояние разговора для следующего пользователя
        await state.finish()


@dp.message_handler(state=QuestionnaireStates.ANSWERING)
async def answer_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        current_question = data['current_question']
        try:
            if current_question.split()[0] == 'underground_nearest' or current_question.split()[0] == 'locality_name':
                answers[current_question.split()[0]] = \
                filtered_df[filtered_df[current_question.split()[0]] == message.text.lower()][
                    'price'].mean()
                print(current_question.split()[0], message.text.lower())
            else:
                answers[current_question.split()[0]] = message.text.lower()

            if COLUMNS_FOR_TG[current_question] == 'int':
                answers[current_question.split()[0]] = int(message.text)
            elif COLUMNS_FOR_TG[current_question] == 'float':
                if ',' in message.text:
                    message.text = message.text.replace(',', '.')
                answers[current_question.split()[0]] = float(message.text)

            data["questions"].pop(0)
        except:
            await message.answer(f'Пожалуйста, введите корректное значение')

    await ask_next_question(message, state)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
