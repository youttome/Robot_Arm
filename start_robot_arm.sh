#!/usr/bin/env bash

set -Eeuo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${WORKSPACE_DIR}/log/startup"
TIMEOUT_SECONDS="${STARTUP_TIMEOUT_SECONDS:-60}"

mkdir -p "${LOG_DIR}"

if [[ -z "${ROS_DISTRO:-}" ]]; then
    echo "ERROR: ROS_DISTRO is not set. Source your ROS 2 installation first."
    exit 1
fi

# shellcheck source=/dev/null
if [[ -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]]; then
    set +u
    source "/opt/ros/${ROS_DISTRO}/setup.bash"
    set -u
fi

if [[ ! -f "${WORKSPACE_DIR}/install/setup.bash" ]]; then
    echo "ERROR: ${WORKSPACE_DIR}/install/setup.bash was not found. Build the workspace first."
    exit 1
fi

set +u
source "${WORKSPACE_DIR}/install/setup.bash"
set -u

gazebo_pid=""
control_pid=""

cleanup() {
    echo
    echo "Stopping startup processes..."
    [[ -n "${control_pid}" ]] && kill "${control_pid}" 2>/dev/null || true
    [[ -n "${gazebo_pid}" ]] && kill "${gazebo_pid}" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

wait_for_topic() {
    local topic="$1"
    local deadline=$((SECONDS + TIMEOUT_SECONDS))

    while (( SECONDS < deadline )); do
        if ros2 topic list 2>/dev/null | grep -Fxq "${topic}"; then
            return 0
        fi
        sleep 1
    done

    return 1
}

wait_for_service() {
    local service="$1"
    local deadline=$((SECONDS + TIMEOUT_SECONDS))

    while (( SECONDS < deadline )); do
        if ros2 service list 2>/dev/null | grep -Fxq "${service}"; then
            return 0
        fi
        sleep 1
    done

    return 1
}

wait_for_controllers() {
    local deadline=$((SECONDS + TIMEOUT_SECONDS))
    local controllers

    while (( SECONDS < deadline )); do
        controllers="$(ros2 control list_controllers 2>/dev/null || true)"

        if grep -Eq '^arm_control[[:space:]].*[[:space:]]active([[:space:]]|$)' <<<"${controllers}" \
            && grep -Eq '^gripper_control[[:space:]].*[[:space:]]active([[:space:]]|$)' <<<"${controllers}" \
            && grep -Eq '^joint_state_broadcaster[[:space:]].*[[:space:]]active([[:space:]]|$)' <<<"${controllers}"; then
            printf '%s\n' "${controllers}"
            return 0
        fi

        sleep 1
    done

    printf '%s\n' "${controllers:-No controller information available.}"
    return 1
}

echo "[1/4] Starting Gazebo and spawning the robot..."
ros2 launch arduino_model display.gazebo.launch.py \
    >"${LOG_DIR}/gazebo.log" 2>&1 &
gazebo_pid=$!

if wait_for_topic "/clock"; then
    echo "[1/4] Gazebo launch done."
else
    echo "ERROR: Gazebo did not publish /clock within ${TIMEOUT_SECONDS} seconds."
    exit 1
fi

echo "[2/4] Starting ros2_control..."
ros2 launch arduino_controller control.launch.py \
    >"${LOG_DIR}/control.log" 2>&1 &
control_pid=$!

if ! wait_for_service "/controller_manager/list_controllers"; then
    echo "ERROR: controller_manager did not become available within ${TIMEOUT_SECONDS} seconds."
    exit 1
fi

echo "[2/4] Control joints launch done."
echo "[3/4] Checking controller connections with Gazebo..."
if wait_for_controllers; then
    echo "[3/4] All joint controllers are active and connected."
else
    echo "ERROR: Expected controllers did not become active within ${TIMEOUT_SECONDS} seconds."
    exit 1
fi

echo "[4/4] Starting MoveIt and RViz..."
echo "MoveIt/RViz started. Logs: ${LOG_DIR}"
moveit_status=0
ros2 launch arduino_moveit moveit.launch.py || moveit_status=$?
exit "${moveit_status}"