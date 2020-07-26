import logging
from datetime import datetime, timedelta
import sys
import os
import glob

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

sys.path.append("/usr/local/airflow/lib/")

from extra_functions import custom_function

logger = logging.getLogger(__name__)

sys_load_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

# specific dag arguments
dag_args = {
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': [''],
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'trigger_rule': 'all_success',
    'email_on_failure': False,
    'email_on_retry': False,
}

test_dag = DAG(
    dag_id='demo_dag',
    default_args=dag_args,
    description='A DAG for every day 4AM UTC',
    schedule_interval='0 4 * * *',
)


def merge_files():
    read_files = glob.glob("/usr/local/airflow/files/*.txt")
    print(read_files)
    with open("/usr/local/airflow/files/result.txt", "ba+") as outfile:
        for f in read_files:
            logger.debug('Read file ' + f)
            with open(f, "rb") as infile:
                outfile.write(infile.read())

with test_dag:
    extract_data = PythonOperator(
        task_id='extract_data',
        python_callable=custom_function,
        op_kwargs={
            # params to execute method
        },
        retries=0,
        test_dag=test_dag
    )

    extract_data_two_data = BashOperator(
        task_id='extract_data_two_data',
        bash_command=(
            f'''ls -l'''
        ),
        retries=3,
        test_dag=test_dag,
    )

    transform_data = BashOperator(
        task_id='transform_data',
        bash_command=(
            f'''ls -l'''
        ),
        retries=1,
        test_dag=test_dag
    )

    transform_data_two = BashOperator(
        task_id='transform_data_two',
        bash_command=(
            f'''pwd'''
        ),
        retries=0,
        test_dag=test_dag
    )

    merge_files_operator = PythonOperator(
        task_id='merge_files_operator',
        python_callable=merge_files,
        op_kwargs={
            # params to execute method
        },
        retries=0,
        test_dag=test_dag
    )

with test_dag:
    start_pipeline = DummyOperator(task_id='start_pipeline')
    notify = DummyOperator(task_id='notify')
    finish_pipeline = DummyOperator(task_id='finish_pipeline')


start_pipeline >> [extract_data, extract_data_two_data] >> transform_data >> merge_files_operator >> transform_data_two >> finish_pipeline >> notify