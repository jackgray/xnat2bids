

def addSequence():
        with_bids = {'series_description': i, 'bidsname': bidsname}
        generated_bids.append(with_bids)
        just_added_bids.append(i)
        generated_d2b.append(with_d2b)
        just_added_d2b.append(i)


def discern_sequences(not_in_map, map_files):
 
    for series in not_in_map:
        print("\nAdding", series, "to ", map_file)
        taskname = ''
        run_number = ''
        series = series.lower()
        
        # discern funcs
        if any(x in series for x in funcs) and not any(x in series for x in fmaps):
            if re.match('func_mux.$', series):
                taskname = 'untitled'
            elif series.startswith('func_mux') or series.startswith('func_epi'):
                taskname = series.split('_')[2]
            else:
                taskname = series.split('_')[1]
            for element in series.split('_'):
                if element.isdigit():
                    if not element.isalpha():
                        run_number = element
            if any(y in taskname for y in rs_names) and not any(z in taskname for z in not_rs):
                sidecar_name = taskname
                taskname = 'rest'
            dataType = "func"
            modalityLabel = "bold"
            if len(run_number) > 0: 
                customLabels = 'task-' + taskname + '_run-0' + run_number

            else:
                customLabels = 'task-' + taskname
            sidecar_name = taskname
            for_d2b = {  "dataType": dataType, "modatlityLabel": modalityLabel, "customLabels": customLabels, "criteria": { "SeriesDescription": i}, "sidecarChanges": { "TaskName": sidecar_name} }
            addSequence()
        
        # discern ASL
        elif 'asl' in series:
            bidsname = 'asl'
            addSequence()

        # discern DTI
        elif 'dti' in series:
            bidsname = 'dti'
            addSequence()

        elif any(x in series for x in t1s) and not any(x in series for x in funcs):
            bidsname = 'T1w'
            addSequence()

        # Find t2s but exclude funcs that have T2 in the name (ASSET2)
        elif any(x in series for x in t2s) and not any(x in series for x in funcs):
            bidsname = 'T2w'
            addSequence()
        else:
            else_bids.append(series)
