# -*- coding: utf-8 -*-
from decimal import Decimal

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import MultipleLocator
import seaborn as sns



def set_gantt_color(data, palette=None, **kwargs):
    # data.insert(0, "color", None)
    color_category = data[data.color_category > 0].drop_duplicates(subset=['color_category'])[
        'color_category'].sort_values()
    color_count = color_category.count()
    current_palette = sns.color_palette(palette, n_colors=color_count)

    # current_palette = plt.cm.get_cmap('Pastel1', len(job_array))

    color_dict = dict((c, p) for c, p in zip(color_category, current_palette))

    # color_dict = {1: (0.6313725490196078, 0.788235294117647, 0.9568627450980393),
    #               2: (0.5529411764705883, 0.8980392156862745, 0.6313725490196078),
    #               3: (1.0, 0.6235294117647059, 0.6078431372549019),
    #               4: (0.8156862745098039, 0.7333333333333333, 1.0), 5: (1.0, 0.996078431372549, 0.6392156862745098)}

    colors = []
    for i in data.index:
        if data.color_category[i] > 0:
            # data.loc[i, "color"] = [frozenset(color_dict[data.color_category[i]])]
            colors.append(color_dict[data.color_category[i]])
        if data.color_category[i] <= 0:
            colors.append(None)
    data.insert(0, "color", colors)
    return data


def gantt(num_jobs, num_vehicles, data_job, data_agv, max_finish=None, show_title=False, show_y_label=True, show_legend=True, text_font_size=8,
          time_font_size=6, title=None, **kwargs):
    """ Plot a gantt chart.
    """
    gantt_labels = {f"Job{job}": f"Job{job}" for job in range(1, num_jobs + 1)}
    gantt_labels |= {f"AGV{agv}": f"AGV{agv}" for agv in range(1, num_vehicles + 1)}
    gantt_labels |= {"empty load": "empty load"}
    # gantt_labels |= {f"AGV{agv}": f"AGV{agv}" for agv in range(1, num_vehicles + 1)}
    # gantt_labels |= {f"AGV{agv}": f"AGV{agv}" for agv in range(1, num_vehicles + 1)}

    ax = plt.gca()
    data_job.insert(0, "y_label", None)
    for i in data_job.index:
        data_job.loc[i, "y_label"] = "$m_{" + str(data_job.machine[i]) + "}$"

    data_job.insert(0, "y_offset", data_job["y_label"].rank(method='dense', ascending=True))
    # data_job.y_offset = data_job.y_offset - 1
    bar_height = 0.65
    text_margin = max_finish / 82 - 0.1
    data_job.sort_values(by='label', ascending=True, inplace=True)
    for i in data_job.index:
        if data_job.bar_type[i] == "PlaceholderBar":
            ax.broken_barh([(data_job.start[i], data_job.finish[i] - data_job.start[i])], (data_job.y_offset[i] - bar_height / 2, bar_height),
                           facecolor=None, edgecolor=None)

        elif data_job.bar_type[i] == "NormalBar":
            ax.broken_barh([(data_job.start[i], data_job.finish[i] - data_job.start[i])], (data_job.y_offset[i] - bar_height / 2, bar_height),
                           facecolor=data_job.color[i], edgecolor="gray", label=gantt_labels[data_job.label[i]])
            gantt_labels[data_job.label[i]] = "_nolegend_"

            ax.text((data_job.finish[i] + data_job.start[i]) / 2, data_job.y_offset[i],
                    data_job.text[i], verticalalignment="center", horizontalalignment="center", color="black", fontsize=text_font_size)

            ax.text(data_job.start[i] + text_margin, data_job.y_offset[i] - bar_height / 2,
                    "{0}".format(Decimal(data_job.start[i]).quantize(Decimal("0"), rounding="ROUND_HALF_UP")), verticalalignment="bottom",
                    horizontalalignment="center", color="black", fontsize=time_font_size)
            ax.text(data_job.finish[i] - text_margin, data_job.y_offset[i] - bar_height / 2,
                    "{0}".format(Decimal(data_job.finish[i]).quantize(Decimal("0"), rounding="ROUND_HALF_UP")), verticalalignment="bottom",
                    horizontalalignment="center", color="black", fontsize=time_font_size)

    agv_bar_height = 0.4
    data_agv.sort_values(by='agv', ascending=True, inplace=True)
    for i in data_agv.index:
        if data_agv.finish[i] - data_agv.start[i] > 0:
            x = [data_agv.start[i], data_agv.finish[i]]
            y = [data_agv.start_m[i], data_agv.end_m[i]]
            if data_agv.color_category[i] > 0:
                if data_agv.agv[i] == 1:
                    ax.plot(x, y, linestyle='-', color=data_agv.color[i], linewidth=1, marker=None, markersize=1.5, label=None)
                    # gantt_labels["AGV1"] = "_nolegend_"
                    ax.broken_barh([(data_agv.start[i], data_agv.finish[i] - data_agv.start[i])], (-2 - agv_bar_height / 2, agv_bar_height),
                                   facecolor=data_agv.color[i], linestyle='-', edgecolor="gray")

                else:
                    ax.plot(x, y, linestyle='--', color=data_agv.color[i], linewidth=1, marker=None, markersize=1.5, label=None)
                    # gantt_labels["AGV2"] = "_nolegend_"
                    ax.broken_barh([(data_agv.start[i], data_agv.finish[i] - data_agv.start[i])], (-1 - agv_bar_height / 2, agv_bar_height),
                                   facecolor=data_agv.color[i], linestyle='--', edgecolor="gray")
            elif data_agv.color_category[i] == 0:
                if data_agv.agv[i] == 1:
                    ax.plot(x, y, linestyle='-', color='black', linewidth=1, marker=None, markersize=1.5, label=gantt_labels["AGV1"])
                    gantt_labels["AGV1"] = "_nolegend_"
                    ax.broken_barh([(data_agv.start[i], data_agv.finish[i] - data_agv.start[i])], (-2 - agv_bar_height / 2, agv_bar_height),
                                   facecolor='white', linestyle='-', edgecolor="gray")
                else:
                    ax.plot(x, y, linestyle='--', color='black', linewidth=1, marker=None, markersize=1.5, label=gantt_labels["AGV2"])
                    gantt_labels["AGV2"] = "_nolegend_"
                    ax.broken_barh([(data_agv.start[i], data_agv.finish[i] - data_agv.start[i])], (-1 - agv_bar_height / 2, agv_bar_height),
                                   facecolor='white', linestyle='--', edgecolor="gray",  label=gantt_labels["empty load"])
                    gantt_labels["empty load"] = "_nolegend_"
            else:
                if data_agv.agv[i] == 1:
                    ax.plot(x, y, linestyle='-', color='white', linewidth=1, marker=None, markersize=1.5, label=None)
                    # gantt_labels["AGV1"] = "_nolegend_"
                else:
                    ax.plot(x, y, linestyle='--', color='white', linewidth=1, marker=None, markersize=1.5, label=None)
                    # gantt_labels["AGV2"] = "_nolegend_"

    plt.tick_params(axis='both', which='major', labelsize=time_font_size)

    # Set xticks
    if max_finish is not None:
        ax.set_xlim(0, max_finish)
        if max_finish < 200:
            ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
        elif max_finish < 300:
            ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(10))
        elif max_finish < 600:
            ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(20))
        else:
            ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(30))

    # Set yticks
    if show_y_label is True:
        labels = data_job.drop_duplicates(subset=['y_label'])['y_label'].sort_values(ascending=True).to_list()

        labels.insert(0, "Depot")
        labels.insert(0, "Agv2")
        labels.insert(0, "Agv1")
        ax.set_yticks(range(-2, len(labels) - 2))
        ax.set_yticklabels(labels)
    else:
        ax.set_yticks([])

    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    # Set title
    if show_title is True:
        ax.set_title(title, {'fontsize': 10})
    if show_legend is True:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=12, fontsize=time_font_size, borderpad=0.3, labelspacing=0.8, columnspacing=0.8)

