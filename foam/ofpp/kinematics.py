import re

def extract_pos_vel(
    fpath: str,
    time_pattern=r"^Time = [0-9]*.*$",
    pos_pattern=r"\s*Centre of mass:.*",
    vel_pattern=r"\s*Linear velocity:.*",
):
    time_re = re.compile(time_pattern, re.IGNORECASE)
    pos_re = re.compile(pos_pattern, re.IGNORECASE)
    vel_re = re.compile(vel_pattern, re.IGNORECASE)
    time = 0
    position = [0.0, 0.0, 0.0]
    velocity = [0.0, 0.0, 0.0]
    with open(fpath, "r") as fh:
        for line in fh:
            line = line.rstrip()
            if time_re.match(line):
                # print(time, position, velocity)
                if not time == 0:
                    yield (
                        f"{time},{','.join(map(str, position))},{','.join(map(str, velocity))}\n"
                    )
                time = float(line.split("=")[-1])
            if pos_re.match(line):
                position = list(
                    map(
                        float,
                        line.split(":")[-1]
                        .replace("(", "")
                        .replace(")", "")
                        .split(" ")[-3:],
                    )
                )
            if vel_re.match(line):
                velocity = list(
                    map(
                        float,
                        line.split(":")[-1]
                        .replace("(", "")
                        .replace(")", "")
                        .split(" ")[-3:],
                    )
                )


def write_pos_vel(
    data_iter,
    fpath="kinematics.csv",
):
    with open(fpath, "w") as out_fh:
        out_fh.write("time,pos_x,pos_y,pos_z,vel_x,vel_y,vel_z\n")
        for line in data_iter:
            out_fh.write(line)

