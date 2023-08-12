tail -n 1000 bot.log > tmp.log; tail -n 1000 tmp.log > bot.log; rm tmp.log
tail -n 1000 twitter.db > tmp.log; tail -n 1000 tmp.log > twitter.db; rm tmp.log
tail -n 1000 geckodriver.log > tmp.log; tail -n 1000 tmp.log > geckodriver.log; rm tmp.log
