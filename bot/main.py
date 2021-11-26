import asyncio
import aiogram
from urllib.parse import urlparse
from webshot import init_driver, load_page, do_screenshot
from config import TOKEN

bot = aiogram.Bot(token=TOKEN, parse_mode='html')
dp = aiogram.Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_start(message: aiogram.types.Message):
	username = message.from_user.username
	if username:
		user = "@" + username
	else:
		user = message.from_user.first_name

	await message.answer(f'Привет, {user}, отправь мне ссылку на сайт и я сделаю полный скриншот!')


@dp.message_handler(content_types=aiogram.types.ContentTypes.TEXT)
async def proceed_link(message: aiogram.types.Message):
	parse_result = urlparse(message.text)
	if parse_result.scheme in ('http', 'https'):
		loop = asyncio.get_event_loop()

		m = await message.answer('<b>Загружаю веб-драйвер...</b>')
		driver = await loop.run_in_executor(None, init_driver)

		await m.edit_text('<b>Скачиваю страницу и прогружаю элементы...</b>')
		await loop.run_in_executor(None, load_page, driver, message.text)

		await m.edit_text('<b>Делаю скриншот...</b>')
		file = await loop.run_in_executor(None, do_screenshot, driver)

		await m.edit_text('<b>Готово!</b>')
		await bot.send_document(message.from_user.id, file, caption=f'Скриншот страницы {message.text}')
		driver.quit()
	else:
		await message.answer('Пожалуйста, вводи ссылку с указанием http или https')

asyncio.run(dp.start_polling())
