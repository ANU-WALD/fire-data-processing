# Submit several jobs at once:
# for year in (2016, 2017):
#     for tile in 'h27v11 h27v12 h28v11 h28v12 h28v13 h29v10 h29v11 h29v12 h29v13 h30v10 h30v11 h30v12 h30v13 h31v10 h31v11 h31v12 h32v10 h32v11'.split():
#         print('qsub -F "{} {}" onetile.qsub'.format(year, tile))
qsub -F "2016 h27v11" onetile.qsub
qsub -F "2016 h27v12" onetile.qsub
qsub -F "2016 h28v11" onetile.qsub
qsub -F "2016 h28v12" onetile.qsub
qsub -F "2016 h28v13" onetile.qsub
qsub -F "2016 h29v10" onetile.qsub
qsub -F "2016 h29v11" onetile.qsub
qsub -F "2016 h29v12" onetile.qsub
qsub -F "2016 h29v13" onetile.qsub
qsub -F "2016 h30v10" onetile.qsub
qsub -F "2016 h30v11" onetile.qsub
qsub -F "2016 h30v12" onetile.qsub
qsub -F "2016 h30v13" onetile.qsub
qsub -F "2016 h31v10" onetile.qsub
qsub -F "2016 h31v11" onetile.qsub
qsub -F "2016 h31v12" onetile.qsub
qsub -F "2016 h32v10" onetile.qsub
qsub -F "2016 h32v11" onetile.qsub
qsub -F "2017 h27v11" onetile.qsub
qsub -F "2017 h27v12" onetile.qsub
qsub -F "2017 h28v11" onetile.qsub
qsub -F "2017 h28v12" onetile.qsub
qsub -F "2017 h28v13" onetile.qsub
qsub -F "2017 h29v10" onetile.qsub
qsub -F "2017 h29v11" onetile.qsub
qsub -F "2017 h29v12" onetile.qsub
qsub -F "2017 h29v13" onetile.qsub
qsub -F "2017 h30v10" onetile.qsub
qsub -F "2017 h30v11" onetile.qsub
qsub -F "2017 h30v12" onetile.qsub
qsub -F "2017 h30v13" onetile.qsub
qsub -F "2017 h31v10" onetile.qsub
qsub -F "2017 h31v11" onetile.qsub
qsub -F "2017 h31v12" onetile.qsub
qsub -F "2017 h32v10" onetile.qsub
qsub -F "2017 h32v11" onetile.qsub
