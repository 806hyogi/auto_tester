*** Settings ***
Library    remote.py
Library    remote
Library    DateTime

*** Keywords ***
Get Datetime
    ${DATE}=      Get Current Date      exclude_millis=yes
    ${CONVERT}=      Convert Date      ${DATE}      result_format=%Y%m%d%H%M
    RETURN    ${CONVERT}

set_host_info
    ${lsim}    ${rsim}    Get Host Info
    RETURN 

get_scenario_list
    [Arguments]    ${DIR}
    #test_list.cfg에서 시나리오 목록(경로) 가져오기
    ${scenario_list}    Scenario List    ${DIR}
    RETURN    ${scenario_list}

get_scenario_file
    #시나리오 경로에서 xml파일 경로 가져오기
    [Arguments]    ${DIR}    ${TYPE}
    ${scenario_file}    Scenario File    ${DIR}    ${TYPE}
    RETURN    ${scenario_file}

upload_scenario
    #xml파일을 업로드
    [Arguments]    ${HOST_INFO}    ${LOCAL_PATH}    ${REMOTE_PATH}
    Open Connection    ${HOST_INFO['HOST']}    ${HOST_INFO['PORT']}    ${HOST_INFO['USER']}    ${HOST_INFO['PW']}
    Open Sftp Connection
    Upload File    ${LOCAL_PATH}    ${REMOTE_PATH}
    Close Connection

exec_scenario
    [Arguments]    ${HOST_INFO}    ${COMMAND}
    Open Connection    ${HOST_INFO['HOST']}    ${HOST_INFO['PORT']}    ${HOST_INFO['USER']}    ${HOST_INFO['PW']}
    ${server_output}    Exec Sipp    ${COMMAND}
    Log    ${server_output[0]}
    Log    ${server_output[1]}
    Close Connection
    RETURN    ${server_output}

wait_end
    [Arguments]    ${HOST_INFO}    ${PID}    
    Open Connection    ${HOST_INFO['HOST']}    ${HOST_INFO['PORT']}    ${HOST_INFO['USER']}    ${HOST_INFO['PW']}
    Check End    ${PID}
    Close Connection

make_log_dir
    [Arguments]    ${DIR}    ${TIME_NOW}
    Make Dir    ${DIR}    ${TIME_NOW}
    RETURN    ${DIR}/${TIME_NOW}

mv_log_file
    [Arguments]    ${HOST_INFO}    ${REMOTE_PATH}    ${LOCAL_PATH}
    Open Connection    ${HOST_INFO['HOST']}    ${HOST_INFO['PORT']}    ${HOST_INFO['USER']}    ${HOST_INFO['PW']}
    Open Sftp Connection
    ${log_files}    Get Remote Log File    ${REMOTE_PATH}    ""
    FOR    ${log_file}    IN    @{log_files}
        Download File    ${log_file}    ${LOCAL_PATH}
    END
    Close Connection

delete_all_file
    [Arguments]    ${HOST_INFO}    ${CMD}
    Open Connection    ${HOST_INFO['HOST']}    ${HOST_INFO['PORT']}    ${HOST_INFO['USER']}    ${HOST_INFO['PW']}
    Input Cmd    ${CMD}
    Close Connection

write_receive_log
    [Arguments]    ${DIR}
    ${log_file_list}    Get Local Log File    ${DIR}    messages
    Log    ${log_file_list}
    FOR    ${log_file}    IN    @{log_file_list}
        Make Received Log    ${log_file}
    END

check_scenario_rule
    [Arguments]    ${DIR}    ${TYPE}
    Check Rules    ${DIR}    ${TYPE}

make_recent_log
    [Arguments]    ${DIR}
    Create Recent Log    ${DIR}