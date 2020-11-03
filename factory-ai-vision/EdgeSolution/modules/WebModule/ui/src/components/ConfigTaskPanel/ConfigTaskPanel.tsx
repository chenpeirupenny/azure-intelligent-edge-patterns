import React, { useEffect, useMemo, useState } from 'react';
import { useHistory } from 'react-router-dom';
import * as R from 'ramda';
import {
  Panel,
  Stack,
  PrimaryButton,
  DefaultButton,
  Dropdown,
  TextField,
  PanelType,
  getTheme,
} from '@fluentui/react';
import { useSelector, useDispatch } from 'react-redux';
import Axios from 'axios';

import { State } from 'RootStateType';
import { getCameras, cameraOptionsSelectorFactoryInConfig } from '../../store/cameraSlice';
import { partOptionsSelectorFactory, getParts } from '../../store/partSlice';
import { ProjectData, InferenceMode } from '../../store/project/projectTypes';
import { getTrainingProject, trainingProjectOptionsSelectorFactory } from '../../store/trainingProjectSlice';
import { getAppInsights } from '../../TelemetryService';
import { getConfigure, thunkPostProject } from '../../store/project/projectActions';
import { getScenario } from '../../store/scenarioSlice';
import { AdvancedOptions } from './AdvancedOptions';

const sendTrainInfoToAppInsight = async (selectedParts): Promise<void> => {
  const { data: images } = await Axios.get('/api/images/');

  const selectedPartIds = selectedParts.map((e) => e.id);
  const interestedImagesLength = images.filter((e) => selectedPartIds.includes(e.part)).length;
  const appInsight = getAppInsights();
  if (appInsight)
    appInsight.trackEvent({
      name: 'train',
      properties: {
        images: interestedImagesLength,
        parts: selectedParts.length,
        source: '',
      },
    });
};

const { palette } = getTheme();

const panelStyles = {
  root: {
    height: 'calc(100% - 48px)',
    top: '46px',
  },
  main: {
    backgroundColor: palette.neutralLighter,
  },
  footerInner: {
    backgroundColor: palette.neutralLighter,
  },
};

type ConfigTaskPanelProps = {
  isOpen: boolean;
  onDismiss: () => void;
  projectData: ProjectData;
  trainingProjectOfSelectedScenario?: number;
  isEdit?: boolean;
};

export const ConfigTaskPanel: React.FC<ConfigTaskPanelProps> = ({
  isOpen,
  onDismiss,
  projectData: initialProjectData,
  trainingProjectOfSelectedScenario = null,
  isEdit = false,
}) => {
  const [projectData, setProjectData] = useState(initialProjectData);
  useEffect(() => {
    setProjectData(initialProjectData);
  }, [initialProjectData]);

  const cameraOptionsSelectorInConfig = useMemo(
    () => cameraOptionsSelectorFactoryInConfig(projectData.trainingProject),
    [projectData.trainingProject],
  );
  const cameraOptions = useSelector(cameraOptionsSelectorInConfig);
  const selectedCameraOptions = useMemo(
    () => cameraOptions.filter((e) => projectData.cameras.includes(e.key)),
    [cameraOptions, projectData.cameras],
  );

  const partOptionsSelector = useMemo(() => partOptionsSelectorFactory(projectData.trainingProject), [
    projectData.trainingProject,
  ]);
  const partOptions = useSelector(partOptionsSelector);
  const selectedPartOptions = useMemo(() => partOptions.filter((e) => projectData.parts.includes(e.key)), [
    partOptions,
    projectData.parts,
  ]);

  const trainingProjectOptionsSelector = trainingProjectOptionsSelectorFactory(
    isEdit ? initialProjectData.trainingProject : trainingProjectOfSelectedScenario,
  );
  const trainingProjectOptions = useSelector(trainingProjectOptionsSelector);
  const scenarios = useSelector((state: State) => state.scenario);
  const dispatch = useDispatch();
  const history = useHistory();
  const [deploying, setdeploying] = useState(false);

  function onChange<K extends keyof P, P = ProjectData>(key: K, value: P[K]) {
    const cloneProject = R.clone(projectData);
    (cloneProject as any)[key] = value;
    if (key === 'trainingProject') {
      // Because demo parts and demo camera can only be used in demo training project(6 scenarios)
      // We should reset them every time the training project is changed
      cloneProject.parts = [];
      cloneProject.cameras = [];

      const relatedScenario = scenarios.find((e) => e.trainingProject === cloneProject.trainingProject);
      if (relatedScenario !== undefined) cloneProject.inferenceMode = relatedScenario.inferenceMode;
      else cloneProject.inferenceMode = InferenceMode.PartDetection;
    } else if (key === 'cameras') {
      cloneProject.SVTCcameras = cloneProject.SVTCcameras.filter((e) => cloneProject.cameras.includes(e));
      cloneProject.recomendedFps = Math.floor(
        cloneProject.totalRecomendedFps / (cloneProject.cameras.length || 1),
      );
    } else if (key === 'parts') {
      cloneProject.SVTCparts = cloneProject.SVTCparts.filter((e) => cloneProject.parts.includes(e));
    } else if (key === 'SVTCisOpen' && !value) {
      cloneProject.SVTCcameras = [];
      cloneProject.SVTCconfirmationThreshold = 0;
      cloneProject.SVTCparts = [];
    }
    setProjectData(cloneProject);
  }

  useEffect(() => {
    dispatch(getParts());
    dispatch(getCameras(true));
    dispatch(getTrainingProject(true));
    dispatch(getScenario());
  }, [dispatch]);

  const onDeployClicked = async () => {
    sendTrainInfoToAppInsight(projectData.parts);

    setdeploying(true);
    const projectId = await dispatch(thunkPostProject(projectData));
    await dispatch(getConfigure((projectId as unknown) as number));
    setdeploying(false);

    onDismiss();
    history.push('/home/deployment');
  };

  const onRenderFooterContent = () => {
    let deployBtnTxt = 'Deploy';
    if (isEdit) deployBtnTxt = 'Redeploy';
    if (deploying) deployBtnTxt = 'Deploying';
    return (
      <Stack tokens={{ childrenGap: 5 }} horizontal>
        <PrimaryButton text={deployBtnTxt} onClick={onDeployClicked} disabled={deploying} />
        <DefaultButton text="Cancel" onClick={onDismiss} />
      </Stack>
    );
  };

  return (
    <Panel
      isOpen={isOpen}
      onDismiss={onDismiss}
      hasCloseButton
      headerText={isEdit ? 'Edit task' : 'Deploy task'}
      onRenderFooterContent={onRenderFooterContent}
      isFooterAtBottom={true}
      type={PanelType.smallFluid}
      styles={panelStyles}
    >
      <Stack tokens={{ childrenGap: 10 }} styles={{ root: { width: '300px' } }}>
        <TextField required value={projectData.name} onChange={(_, newValue) => onChange('name', newValue)} />
        <Dropdown
          label="Model"
          options={trainingProjectOptions}
          required
          selectedKey={projectData.trainingProject}
          onChange={(_, options) => {
            onChange('trainingProject', options.key as number);
          }}
        />
        <Dropdown
          label="Camera"
          multiSelect
          options={cameraOptions}
          required
          selectedKeys={projectData.cameras}
          onChange={(_, option) => {
            onChange(
              'cameras',
              option.selected
                ? [...projectData.cameras, option.key as number]
                : projectData.cameras.filter((key) => key !== option.key),
            );
          }}
        />
        <Dropdown
          label="Objects"
          multiSelect
          options={partOptions}
          required
          selectedKeys={projectData.parts}
          onChange={(_, option) => {
            if (option) {
              onChange(
                'parts',
                option.selected
                  ? [...projectData.parts, option.key as number]
                  : projectData.parts.filter((key) => key !== option.key),
              );
            }
          }}
        />
      </Stack>
      <AdvancedOptions
        projectData={projectData}
        selectedCameraOptions={selectedCameraOptions}
        selectedPartOptions={selectedPartOptions}
        onChange={onChange}
      />
    </Panel>
  );
};