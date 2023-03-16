import os

tiles = ["h27v11", "h27v12", "h28v11", "h28v12", "h28v13", "h29v10", "h29v11", "h29v12", "h29v13", "h30v10", "h30v11", "h30v12", "h31v10", "h31v11", "h31v12", "h32v10", "h32v11"]

if __name__ == "__main__":
    for year in range(2021,2024):
        for tile in tiles:
            print(year, tile)
            os.system('qsub -v "year={0},tile={1}" /g/data/xc0/user/scortechini/github/fire-data-processing/gadi_tasks/au_recurrent_qsubs/au_flam_tiles_rec.qsub'.format(year, tile))
